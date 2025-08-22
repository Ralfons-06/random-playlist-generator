package app.src

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.spotify.sdk.android.auth.AuthorizationClient
import com.spotify.sdk.android.auth.AuthorizationRequest
import com.spotify.sdk.android.auth.AuthorizationResponse
import kotlinx.coroutines.launch
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.Header
import retrofit2.http.POST

// Main Activity
class MainActivity : ComponentActivity() {
    companion object {
        const val REQUEST_CODE = 1337
        const val REDIRECT_URI = "your-app-package://callback"
        const val CLIENT_ID = "YOUR_CLIENT_ID" // Replace with your Spotify Developer Client ID
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            SpotifyAppTheme {
                val navController = rememberNavController()
                val viewModel: SpotifyViewModel = viewModel()

                NavHost(navController = navController, startDestination = "login") {
                    composable("login") {
                        LoginScreen(
                            onLoginClick = { startSpotifyLogin() },
                            isLoggedIn = viewModel.isLoggedIn
                        )

                        // If user becomes logged in, navigate to main screen
                        LaunchedEffect(viewModel.isLoggedIn) {
                            if (viewModel.isLoggedIn) {
                                navController.navigate("main") {
                                    popUpTo("login") { inclusive = true }
                                }
                            }
                        }
                    }

                    composable("main") {
                        MainScreen(
                            onCreatePlaylistClick = { viewModel.createPlaylist() },
                            isCreatingPlaylist = viewModel.isCreatingPlaylist,
                            playlistCreated = viewModel.playlistCreated,
                            playlistName = viewModel.createdPlaylistName
                        )
                    }
                }
            }
        }
    }

    private fun startSpotifyLogin() {
        val builder = AuthorizationRequest.Builder(
            CLIENT_ID,
            AuthorizationResponse.Type.TOKEN,
            REDIRECT_URI
        )

        builder.setScopes(arrayOf("playlist-modify-public", "playlist-modify-private"))
        val request = builder.build()

        AuthorizationClient.openLoginActivity(this, REQUEST_CODE, request)
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)

        if (requestCode == REQUEST_CODE) {
            val response = AuthorizationClient.getResponse(resultCode, data)

            when (response.type) {
                AuthorizationResponse.Type.TOKEN -> {
                    val viewModel = viewModel<SpotifyViewModel>()
                    viewModel.setToken(response.accessToken)
                }
                AuthorizationResponse.Type.ERROR -> {
                    Toast.makeText(this, "Auth error: ${response.error}", Toast.LENGTH_SHORT).show()
                }
                else -> {
                    Toast.makeText(this, "Login canceled", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
}

// Composable for the Login Screen
@Composable
fun LoginScreen(onLoginClick: () -> Unit, isLoggedIn: Boolean) {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center,
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "Welcome to Spotify Playlist Creator",
                style = MaterialTheme.typography.headlineSmall
            )

            Spacer(modifier = Modifier.height(24.dp))

            Button(
                onClick = onLoginClick,
                enabled = !isLoggedIn
            ) {
                Text("Login with Spotify")
            }
        }
    }
}

// Composable for the Main Screen
@Composable
fun MainScreen(
    onCreatePlaylistClick: () -> Unit,
    isCreatingPlaylist: Boolean,
    playlistCreated: Boolean,
    playlistName: String
) {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center,
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "You're logged in!",
                style = MaterialTheme.typography.headlineSmall
            )

            Spacer(modifier = Modifier.height(24.dp))

            Button(
                onClick = onCreatePlaylistClick,
                enabled = !isCreatingPlaylist
            ) {
                Text("Create New Playlist")
            }

            Spacer(modifier = Modifier.height(16.dp))

            if (isCreatingPlaylist) {
                CircularProgressIndicator()
            }

            if (playlistCreated) {
                Text("Playlist '$playlistName' created successfully!")
            }
        }
    }
}

// ViewModel for handling Spotify interactions
class SpotifyViewModel : ViewModel() {
    private val spotifyService by lazy {
        Retrofit.Builder()
            .baseUrl("https://api.spotify.com/v1/")
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(SpotifyService::class.java)
    }

    var token by mutableStateOf("")
        private set

    var isLoggedIn by mutableStateOf(false)
        private set

    var isCreatingPlaylist by mutableStateOf(false)
        private set

    var playlistCreated by mutableStateOf(false)
        private set

    var createdPlaylistName by mutableStateOf("")
        private set

    fun setToken(accessToken: String) {
        token = accessToken
        isLoggedIn = true
    }

    fun createPlaylist() {
        isCreatingPlaylist = true
        playlistCreated = false

        viewModelScope.launch {
            try {
                val playlistName = "My Awesome Playlist ${System.currentTimeMillis() / 1000}"
                val request = CreatePlaylistRequest(
                    name = playlistName,
                    public = true,
                    description = "Created with my custom app"
                )

                // Get user ID first (in a real app you'd cache this)
                val userProfile = getUserProfile()
                val userId = userProfile?.id ?: return@launch

                // Create the playlist
                val response = spotifyService.createPlaylist(
                    "Bearer $token",
                    userId,
                    request
                )

                if (response.id != null) {
                    createdPlaylistName = playlistName
                    playlistCreated = true
                }
            } catch (e: Exception) {
                // Handle error
            } finally {
                isCreatingPlaylist = false
            }
        }
    }

    private suspend fun getUserProfile(): UserProfile? {
        return try {
            spotifyService.getCurrentUserProfile("Bearer $token")
        } catch (e: Exception) {
            null
        }
    }
}

// API Models and Service
data class CreatePlaylistRequest(
    val name: String,
    val public: Boolean,
    val description: String
)

data class PlaylistResponse(
    val id: String?,
    val name: String?,
    val external_urls: Map<String, String>?
)

data class UserProfile(
    val id: String,
    val display_name: String?
)

interface SpotifyService {
    @POST("users/{user_id}/playlists")
    suspend fun createPlaylist(
        @Header("Authorization") auth: String,
        @Path("user_id") userId: String,
        @Body request: CreatePlaylistRequest
    ): PlaylistResponse

    @GET("me")
    suspend fun getCurrentUserProfile(
        @Header("Authorization") auth: String
    ): UserProfile
}

// Theme
@Composable
fun SpotifyAppTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = darkColorScheme(
            primary = Color(0xFF1DB954),      // Spotify green
            background = Color(0xFF191414),   // Spotify black
            surface = Color(0xFF191414),
            onPrimary = Color.White,
            onBackground = Color.White,
            onSurface = Color.White
        ),
        content = content
    )
}