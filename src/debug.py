import arcade


class Debug:
    debug_dict = {}
    text_objects = []
    initialized = False

    @staticmethod
    def _initialize():
        if Debug.initialized:
            return

        MAX_DEBUG_LINES = 20
        for i in range(MAX_DEBUG_LINES):
            Debug.text_objects.append(
                arcade.Text(
                    "",
                    0,
                    0,
                    arcade.csscolor.WHITE,
                    18,
                )
            )
        Debug.initialized = True

    @staticmethod
    def update(key: str, text: str):
        Debug.debug_dict[key] = text

    @staticmethod
    def render(x: float, y: float):
        if not Debug.initialized:
            print("Debug.render called before Debug._initialize. Skipping render.")
            return

        text_object_index = 0
        for key, text_value in Debug.debug_dict.items():
            if text_object_index < len(Debug.text_objects):
                text_object = Debug.text_objects[text_object_index]
                text_object.text = f"{key}: {text_value}"
                text_object.x = x
                text_object.y = y
                text_object.draw()
                y += 20
                text_object_index += 1
            else:
                print(f"Warning: Ran out of pre-allocated debug text objects for key: {key}")

        while text_object_index < len(Debug.text_objects):
            Debug.text_objects[text_object_index].text = ""
            text_object_index += 1 