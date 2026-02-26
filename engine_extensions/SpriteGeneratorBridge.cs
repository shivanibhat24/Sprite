// ============================================================
//  Sprite! — Unity Extension
//  File: SpriteGeneratorBridge.cs
//  Place in: Assets/Editor/SpriteGenerator/
//
//  This script connects Unity's Editor to the locally running
//  Sprite! server (http://localhost:7777) and lets you generate
//  sprites directly inside the Unity Editor.
// ============================================================

using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;
using System.IO;
using System.Text;
using System.Collections;

public class SpriteGeneratorWindow : EditorWindow
{
    private string _prompt         = "pixel warrior character fire";
    private string _assetType      = "sprite";
    private string _palette        = "magic";
    private int    _size           = 64;
    private bool   _include3d      = true;
    private string _outputFolder   = "Assets/GeneratedSprites";
    private string _serverUrl      = "http://localhost:7777";
    private string _statusMsg      = "Ready. Make sure server.py is running.";
    private Texture2D _preview     = null;

    [MenuItem("Tools/Sprite! Generator")]
    public static void ShowWindow()
    {
        var w = GetWindow<SpriteGeneratorWindow>("Sprite! Generator");
        w.minSize = new Vector2(340, 480);
    }

    void OnGUI()
    {
        GUILayout.Label("Sprite! — Game Asset Generator", EditorStyles.boldLabel);
        GUILayout.Label("Server: " + _serverUrl, EditorStyles.miniLabel);
        EditorGUILayout.Space(8);

        _prompt      = EditorGUILayout.TextField("Prompt", _prompt);
        _assetType   = EditorGUILayout.TextField("Type (sprite/3d/tilemap/animation/pack)", _assetType);
        _palette     = EditorGUILayout.TextField("Palette", _palette);
        _size        = EditorGUILayout.IntSlider("Size (px)", _size, 16, 512);
        _outputFolder = EditorGUILayout.TextField("Output Folder", _outputFolder);
        _include3d   = EditorGUILayout.Toggle("Include 3D OBJ", _include3d);
        _serverUrl   = EditorGUILayout.TextField("Server URL", _serverUrl);

        EditorGUILayout.Space(8);

        if(GUILayout.Button("⚡ Generate Asset", GUILayout.Height(36)))
            StartGenerate();

        if(GUILayout.Button("📦 Download Full ZIP", GUILayout.Height(28)))
            DownloadZip();

        if(GUILayout.Button("🌐 Open in Browser", GUILayout.Height(28)))
            Application.OpenURL(_serverUrl);

        EditorGUILayout.Space(8);
        EditorGUILayout.HelpBox(_statusMsg, MessageType.Info);

        if(_preview != null)
        {
            GUILayout.Label("Preview:");
            float pw = Mathf.Min(position.width - 20, 200);
            GUILayout.Label(_preview, GUILayout.Width(pw), GUILayout.Height(pw));
        }
    }

    void StartGenerate()
    {
        _statusMsg = "Generating...";
        Repaint();
        EditorCoroutineUtility.StartCoroutine(GenerateCoroutine(), this);
    }

    IEnumerator GenerateCoroutine()
    {
        string fullPrompt = $"{_prompt} {_palette} {_size}px";
        string json = $"{{\"prompt\":\"{fullPrompt}\"}}";
        var endpoint = _serverUrl + "/api/generate/" + _assetType;
        var req = new UnityWebRequest(endpoint, "POST");
        byte[] bodyRaw = Encoding.UTF8.GetBytes(json);
        req.uploadHandler   = new UploadHandlerRaw(bodyRaw);
        req.downloadHandler = new DownloadHandlerBuffer();
        req.SetRequestHeader("Content-Type", "application/json");
        yield return req.SendWebRequest();

        if(req.result != UnityWebRequest.Result.Success)
        {
            _statusMsg = "Error: " + req.error;
            Repaint();
            yield break;
        }

        var response = JsonUtility.FromJson<SpriteResponse>(req.downloadHandler.text);
        if(!string.IsNullOrEmpty(response.image_b64))
        {
            byte[] imgBytes = System.Convert.FromBase64String(response.image_b64);
            if(!Directory.Exists(_outputFolder)) Directory.CreateDirectory(_outputFolder);
            string safeName = _prompt.Replace(" ","_").Substring(0, Mathf.Min(20, _prompt.Length));
            string path = $"{_outputFolder}/{safeName}_{_size}.png";
            File.WriteAllBytes(path, imgBytes);
            AssetDatabase.ImportAsset(path);

            // Configure as pixel art sprite
            var ti = AssetImporter.GetAtPath(path) as TextureImporter;
            if(ti != null)
            {
                ti.textureType = TextureImporterType.Sprite;
                ti.filterMode = FilterMode.Point;
                ti.textureCompression = TextureImporterCompression.Uncompressed;
                ti.maxTextureSize = 512;
                ti.SaveAndReimport();
            }

            _preview = new Texture2D(2,2);
            _preview.LoadImage(imgBytes);
            _statusMsg = $"✓ Saved: {path}";
        }
        else
        {
            _statusMsg = "No image returned from server.";
        }
        Repaint();
    }

    void DownloadZip()
    {
        string url = $"{_serverUrl}/api/download/zip";
        // Just open browser to download
        Application.OpenURL(_serverUrl);
        _statusMsg = "Open the browser UI to download ZIP.";
    }

    [System.Serializable]
    class SpriteResponse { public string image_b64; public string format; public string size; }
}
