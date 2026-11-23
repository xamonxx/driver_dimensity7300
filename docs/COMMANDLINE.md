# 🎮 GTA V command line untuk Mali-G615 MC2 (720p, target 30 stabil)

Format launcher: satu argumen per baris. `#` hanya untuk komentar satu baris penuh.
Rentang nilai mengikuti daftar resmi Rockstar.

## Profil 30 fps stabil (disarankan)
```
-shaderQuality 0
-shadowQuality 0
-reflectionQuality 0
-waterQuality 0
-SSAO 0
-postFX 0
-tessellation 0
-grassQuality 0
-particleQuality 0
-textureQuality 0
-anisotropicQualityLevel 0
-fxaa 0
-noInGameDOF
-lodScale 0.3
-cityDensity 0.3
-pedLodBias 0.0
-vehicleLodBias 0.0
```
Pasangkan dengan driver **stable30**, resolusi ±960×432–1280×576, dan Target FPS 30 di launcher.

## Profil 60 fps (hanya bila profil 30 sudah stabil jauh di atas 30)
Sama seperti di atas, ditambah resolusi lebih rendah (±854×384) dan driver **stable60**.

Jangan pakai `-frameLimit`, `-HDStreamingInFlight`, `-shadowLongShadows`, `-hdr`, `-txaa`, atau `-multiSample` di atas 1.
