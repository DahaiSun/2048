package com.example.word2048

import android.os.Bundle
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.animation.Crossfade
import androidx.compose.animation.core.tween
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.view.WindowCompat
import com.google.accompanist.systemuicontroller.rememberSystemUiController
import kotlinx.coroutines.delay

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // 1. Edge-to-Edge Fullscreen
        WindowCompat.setDecorFitsSystemWindows(window, false)

        setContent {
            // 2. Control System Bar Colors
            val systemUiController = rememberSystemUiController()
            SideEffect {
                systemUiController.setSystemBarsColor(
                    color = Color.Transparent,
                    darkIcons = false
                )
            }

            var showSplash by remember { mutableStateOf(true) }

            LaunchedEffect(Unit) {
                delay(2500) // Slightly longer splash usage
                showSplash = false
            }

            Surface(
                modifier = Modifier.fillMaxSize(),
                color = Color.Black // Background color behind WebView
            ) {
                // 3. Smooth Crossfade Transition
                Crossfade(
                    targetState = showSplash,
                    animationSpec = tween(durationMillis = 1000), 
                    label = "SplashTransition"
                ) { isSplashing ->
                    if (isSplashing) {
                        SplashScreen { showSplash = false }
                    } else {
                        GameWebView()
                    }
                }
            }
        }
    }

    @Composable
    fun GameWebView() {
        AndroidView(
            modifier = Modifier.fillMaxSize(),
            factory = { context ->
                WebView(context).apply {
                    layoutParams = android.view.ViewGroup.LayoutParams(
                        android.view.ViewGroup.LayoutParams.MATCH_PARENT,
                        android.view.ViewGroup.LayoutParams.MATCH_PARENT
                    )
                    
                    // 4. Optimized WebView Settings
                    settings.apply {
                        javaScriptEnabled = true
                        domStorageEnabled = true
                        databaseEnabled = true
                        mediaPlaybackRequiresUserGesture = false // Allow BGM to autoplay
                        cacheMode = WebSettings.LOAD_DEFAULT
                        // Performance tweaks
                        setRenderPriority(WebSettings.RenderPriority.HIGH)
                    }
                    
                    webViewClient = WebViewClient()
                    loadUrl("file:///android_asset/www/index.html")
                }
            }
        )
    }
}
