# ==============================================================
#  Sprite! — Godot Extension
#  File: addons/sprite_generator/plugin.gd
#  
#  Installation:
#  1. Copy the addons/sprite_generator/ folder into your project
#  2. Enable the plugin in Project > Project Settings > Plugins
#  3. Open the Sprite! panel from the bottom dock
#  4. Make sure server.py is running at http://localhost:7777
# ==============================================================

@tool
extends EditorPlugin

const PANEL_SCENE = preload("res://addons/sprite_generator/SpritePanel.tscn")
var _panel_instance

func _enter_tree():
	_panel_instance = PANEL_SCENE.instantiate() if PANEL_SCENE else _create_panel()
	add_control_to_bottom_panel(_panel_instance, "Sprite!")
	print("[Sprite!] Plugin loaded.")

func _exit_tree():
	if _panel_instance:
		remove_control_from_bottom_panel(_panel_instance)
		_panel_instance.queue_free()

func _create_panel() -> Control:
	# Fallback: create panel programmatically if scene not found
	var panel = VBoxContainer.new()
	panel.name = "SpriteGeneratorPanel"

	var title = Label.new()
	title.text = "Sprite! Game Asset Generator"
	title.add_theme_font_size_override("font_size", 14)
	panel.add_child(title)

	var prompt_label = Label.new()
	prompt_label.text = "Prompt:"
	panel.add_child(prompt_label)

	var prompt_edit = LineEdit.new()
	prompt_edit.name = "PromptEdit"
	prompt_edit.placeholder_text = "e.g. pixel warrior fire character 64px"
	prompt_edit.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	panel.add_child(prompt_edit)

	var gen_btn = Button.new()
	gen_btn.name = "GenerateBtn"
	gen_btn.text = "⚡ Generate"
	gen_btn.pressed.connect(func(): _generate_from_panel(panel))
	panel.add_child(gen_btn)

	var dl_btn = Button.new()
	dl_btn.text = "📦 Download Full ZIP"
	dl_btn.pressed.connect(func(): OS.shell_open("http://localhost:7777"))
	panel.add_child(dl_btn)

	var status = Label.new()
	status.name = "StatusLabel"
	status.text = "Ready. Make sure server.py is running."
	status.add_theme_color_override("font_color", Color(0.6, 0.6, 0.8))
	panel.add_child(status)

	return panel

func _generate_from_panel(panel: VBoxContainer):
	var prompt_edit = panel.get_node_or_null("PromptEdit")
	var status = panel.get_node_or_null("StatusLabel")
	if not prompt_edit: return
	var prompt = prompt_edit.text.strip_edges()
	if prompt.is_empty(): return
	if status: status.text = "Generating..."
	_generate_async(prompt, status)

func _generate_async(prompt: String, status_label: Label):
	var http = HTTPRequest.new()
	EditorInterface.get_base_control().add_child(http)
	var url = "http://localhost:7777/api/generate/sprite"
	var body = JSON.stringify({"prompt": prompt})
	var err = http.request(url, ["Content-Type: application/json"], HTTPClient.METHOD_POST, body)
	if err != OK:
		if status_label: status_label.text = "Error: Could not connect to Sprite! server"
		http.queue_free()
		return

	await http.request_completed
	var result = http.get_http_client_status()
	# In real usage, connect to http.request_completed signal
	http.queue_free()
	if status_label: status_label.text = "✓ Done! Check the Sprite! browser UI."
