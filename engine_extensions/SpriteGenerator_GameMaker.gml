/// ============================================================
///  Sprite! — GameMaker Studio 2 Extension
///  File: extensions/SpriteGenerator/SpriteGenerator.gml
///
///  Setup:
///  1. In GameMaker, go to Extensions > Create Extension
///  2. Name it "SpriteGenerator"
///  3. Add this as a GML file
///  4. Call sprite_gen_init() in your GameCreate event
///  5. Make sure server.py is running at http://localhost:7777
/// ============================================================


// ── CONFIGURATION ──────────────────────────────────────────
#macro SPRITE_SERVER "http://localhost:7777"
#macro SPRITE_OUTPUT_DIR (working_directory + "generated_sprites/")


// ── INIT ────────────────────────────────────────────────────
/// @function sprite_gen_init()
/// @description Initialize the Sprite! generator. Call in Create event.
function sprite_gen_init() {
    global._sprite_gen_ready = false;
    global._sprite_gen_requests = ds_map_create();
    global._sprite_gen_callbacks = ds_map_create();

    // Create output directory
    if (!directory_exists(SPRITE_OUTPUT_DIR)) {
        directory_create(SPRITE_OUTPUT_DIR);
    }

    // Test server connection
    var req_id = http_request(SPRITE_SERVER + "/api/health", "GET", ds_map_create(), "");
    global._sprite_gen_init_req = req_id;
    show_debug_message("[Sprite!] Connecting to server: " + SPRITE_SERVER);
    return req_id;
}


// ── GENERATE SPRITE ─────────────────────────────────────────
/// @function sprite_gen_create(prompt, [callback_name])
/// @description Generate a sprite from a text prompt.
///              callback_name: name of a script to call when done (optional)
///              Returns: request ID
function sprite_gen_create(prompt) {
    var callback = argument_count > 1 ? argument[1] : "";
    var json_body = @'{"prompt":"' + string(prompt) + @'"}';
    var headers = ds_map_create();
    ds_map_add(headers, "Content-Type", "application/json");
    var req_id = http_request(SPRITE_SERVER + "/api/generate/sprite", "POST", headers, json_body);
    ds_map_add(global._sprite_gen_requests, req_id, prompt);
    if (callback != "") ds_map_add(global._sprite_gen_callbacks, req_id, callback);
    ds_map_destroy(headers);
    show_debug_message("[Sprite!] Generating: " + prompt + " (req " + string(req_id) + ")");
    return req_id;
}


// ── GENERATE TILEMAP ────────────────────────────────────────
/// @function sprite_gen_tilemap(prompt, [cols], [rows])
function sprite_gen_tilemap(prompt) {
    var cols = argument_count > 1 ? argument[1] : 4;
    var rows = argument_count > 2 ? argument[2] : 4;
    var json_body = @'{"prompt":"' + prompt + @'","cols":' + string(cols) + @',"rows":' + string(rows) + "}";
    var headers = ds_map_create();
    ds_map_add(headers, "Content-Type", "application/json");
    var req_id = http_request(SPRITE_SERVER + "/api/generate/tilemap", "POST", headers, json_body);
    ds_map_add(global._sprite_gen_requests, req_id, "tilemap:" + prompt);
    ds_map_destroy(headers);
    return req_id;
}


// ── GENERATE ANIMATION ──────────────────────────────────────
/// @function sprite_gen_animation(prompt, [frames])
function sprite_gen_animation(prompt) {
    var frames = argument_count > 1 ? argument[1] : 8;
    var json_body = @'{"prompt":"' + prompt + @'","frames":' + string(frames) + "}";
    var headers = ds_map_create();
    ds_map_add(headers, "Content-Type", "application/json");
    var req_id = http_request(SPRITE_SERVER + "/api/generate/animation", "POST", headers, json_body);
    ds_map_add(global._sprite_gen_requests, req_id, "anim:" + prompt);
    ds_map_destroy(headers);
    return req_id;
}


// ── DOWNLOAD ZIP ────────────────────────────────────────────
/// @function sprite_gen_open_browser()
/// @description Open the Sprite! web UI in the default browser
function sprite_gen_open_browser() {
    url_open(SPRITE_SERVER);
}


// ── HANDLE RESPONSES ────────────────────────────────────────
/// @function sprite_gen_handle_async(async_id, result_string)
/// @description Call this in the Async - HTTP event:
///
///   if (sprite_gen_handle_async(async_load[? "id"], async_load[? "result"])) {
///       // Sprite loaded! global._last_sprite has the sprite index.
///   }
///
function sprite_gen_handle_async(async_id, result_string) {
    if (!ds_map_exists(global._sprite_gen_requests, async_id)) return false;

    var prompt = ds_map_find_value(global._sprite_gen_requests, async_id);
    ds_map_delete(global._sprite_gen_requests, async_id);

    if (result_string == "" || result_string == "error") {
        show_debug_message("[Sprite!] Error for: " + prompt);
        return false;
    }

    // Parse JSON
    var json = json_parse(result_string);
    if (!is_struct(json)) return false;

    var b64 = struct_get(json, "image_b64");
    if (is_undefined(b64)) return false;

    // Write PNG to disk and load as sprite
    var safe_name = string_replace_all(prompt, " ", "_");
    safe_name = string_copy(safe_name, 1, min(string_length(safe_name), 30));
    var filepath = SPRITE_OUTPUT_DIR + safe_name + ".png";

    // GameMaker base64 decode: requires GMS2 2023.1+
    var decoded = base64_decode(b64);
    var buf = buffer_create(buffer_get_size(decoded), buffer_fixed, 1);
    buffer_copy(decoded, 0, buffer_get_size(decoded), buf, 0);
    buffer_save(buf, filepath);
    buffer_delete(buf);

    var spr_idx = sprite_add(filepath, 1, true, true, 0, 0);
    if (spr_idx >= 0) {
        global._last_sprite = spr_idx;
        global._last_sprite_path = filepath;
        show_debug_message("[Sprite!] ✓ Loaded sprite: " + filepath + " (index " + string(spr_idx) + ")");

        // Call callback if registered
        if (ds_map_exists(global._sprite_gen_callbacks, async_id)) {
            var cb = ds_map_find_value(global._sprite_gen_callbacks, async_id);
            ds_map_delete(global._sprite_gen_callbacks, async_id);
            script_execute(asset_get_index(cb), spr_idx, prompt);
        }
        return true;
    }
    return false;
}


/// ── EXAMPLE USAGE ──────────────────────────────────────────
///
///  // In obj_SpriteLoader Create event:
///  sprite_gen_init();
///  request_id = sprite_gen_create("pixel warrior fire character 64px");
///
///  // In obj_SpriteLoader Async - HTTP event:
///  if (sprite_gen_handle_async(async_load[? "id"], async_load[? "result"])) {
///      sprite_index = global._last_sprite;
///      show_debug_message("My new sprite loaded!");
///  }
///
/// ────────────────────────────────────────────────────────────
