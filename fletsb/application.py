from fletsb import uikit
from fletsb import utils
import flet, os, sys

from fletsb.pages import Editor


class Application:
    def __init__(self, storyboard_file_path:str=None) -> None:

        # Experience data
        self.storyboard_file_path = storyboard_file_path
        self.user_on_edit_state = False # Apply when a project is opened for being edited.
        self.sheet_is_fullscreen = False
        self.bgcolor_opacity_number = 0.9
        self.current_presented_scene = None

        # start flet app cycle.

        if sys.platform == "linux" or sys.platform == "linux2":
            flet.app(target=self.app, assets_dir="assets/", view=flet.AppView.WEB_BROWSER)
        else:
            # flet.app(target=self.app, assets_dir="assets/", view=flet.AppView.WEB_BROWSER)
            flet.app(target=self.app, assets_dir="assets/")

    def app (self, page:flet.Page):
        self.page : flet.Page = page
        # Page properties
        page.theme_mode = flet.ThemeMode.DARK
        page.padding = 0
        page.spacing = 0
        page.bgcolor = flet.colors.TRANSPARENT

        # Page events
        page.on_resize = self.on_page_resize
        page.on_keyboard_event = self.on_keyboard_shortcut

        # Page main stack controls
        self.main_stack = flet.Stack(expand=True)
        page.add(self.main_stack)

        # Page background customisation
        bg_container = flet.Container(
            bgcolor="#151515"
        )
        self.bg_container = bg_container
        self.main_stack.controls.append(bg_container)


        # Holders
        self.main_scene_holder = flet.AnimatedSwitcher(
            content=flet.Text(""),
            duration=1,
            switch_in_curve=flet.AnimationCurve.BOUNCE_IN
        )
        self.main_stack.controls.append(self.main_scene_holder)

        self.sheet_container = flet.Container(
            bgcolor="black",
            border_radius=18,
            visible=False,
            padding=15
        )
        self.main_stack.controls.append(flet.Column([
            flet.Row([self.sheet_container], alignment=flet.MainAxisAlignment.CENTER)
        ], alignment=flet.MainAxisAlignment.CENTER))


        # Set specific page appearance for desktop
        if utils.is_phone_platform() == False and page.web == False:
            if "darwin" in str(sys.platform).lower():
                # if on macOS
                page.window_frameless = True
            else:
                # if Windows
                page.window_title_bar_buttons_hidden = True
                page.window_title_bar_hidden = True
            page.window_min_height = 550
            page.window_min_width = 700
            bg_container.border_radius = 18
            bg_container.opacity = self.bgcolor_opacity_number

        
        page.update()
        page.window_center()
        self.on_page_resize(None)

        # Choose what is the startup scene.
        if self.storyboard_file_path == None:
            self.show_a_scene(flet.Text("No scene!"))
        else:
            project_name = os.path.basename(self.storyboard_file_path.replace(".fletsb", ""))
            e = Editor(project_name=project_name, project_path=self.storyboard_file_path, page=self.page, application_class=self)
            self.editor_scene = e
            self.show_a_scene(scene=e)

        self.page.update()
    

    def show_a_scene (self, scene):
        self.current_presented_scene = scene

        self.main_scene_holder.content = scene
        self.main_scene_holder.update()
    

    def on_page_resize (self, e=None):
        # print(e.__dict__)
        if self.page.width > 450:
            #! if big screen size
            self.sheet_container.width = self.page.width / 1.5
            self.sheet_container.height = self.page.height - 150
        else:
            self.sheet_container.width = self.page.width - 50
            self.sheet_container.height = self.page.height - 150
        
        #! if sheet must be full screen:
        if self.sheet_is_fullscreen:
            self.sheet_container.width = self.page.width
            self.sheet_container.height = self.page.height


        if hasattr(self, 'editor_scene') and self.user_on_edit_state:
            self.editor_scene.editor_canvas_engine.main_col.width = self.page.width / 1.5
            self.editor_scene.editor_canvas_engine.main_col.height = self.page.height - 150
            self.editor_scene.right_section.width = self.page.width - (self.page.width / 1.5) - 50
            self.editor_scene.right_section.height = self.editor_scene.editor_canvas_engine.main_col.height
        
        self.page.update()

    def on_keyboard_shortcut (self, e):
        if str(e.key).lower() == "escape":
            if self.sheet_container.visible == True: self.show_the_sheet = False
        

        # Pass event to current scene
        if self.current_presented_scene != None:
            if hasattr(self.current_presented_scene, "on_keyboard_event"):
                self.current_presented_scene.on_keyboard_event(e)
    

    @property
    def show_the_sheet (self): return self.sheet_container.visible

    @show_the_sheet.setter
    def show_the_sheet(self, value:bool):
        if value == True:
            self.sheet_container.visible = True
            self.main_scene_holder.opacity = 0.3
            self.bg_container.opacity = 0.5
            self.main_scene_holder.disabled = True
        else:
            self.sheet_container.visible = False
            self.main_scene_holder.opacity = 1.0
            self.bg_container.opacity = self.bgcolor_opacity_number
            self.main_scene_holder.disabled = False
            self.sheet_is_fullscreen = False
        
        self.on_page_resize()
        
        self.bg_container.update()
        self.main_scene_holder.update()
        self.sheet_container.update()