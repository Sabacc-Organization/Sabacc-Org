from PIL import ImageGrab, PngImagePlugin
import keyboard
import time

images = []
i = -1

while True:
    keve = keyboard.read_event()
    if keve.event_type == 'down':
        if keve.name == 'e':
            break
        if keve.name == 'c':
            time.sleep(0.1)
            clippy: PngImagePlugin.PngImageFile = ImageGrab.grabclipboard()
            images.append(clippy.copy())
            if len(images) == 2:
                i += 1
                image: PngImagePlugin.PngImageFile = images[0].copy()
                image = image.crop((0, 0, image.size[0], image.size[1]+images[1].size[1]))
                image.paste(images[1], (0, images[0].size[1], images[0].size[0], images[0].size[1]+images[1].size[1]))
                image = image.rotate(-90, expand=True)
                image.save('dark/i'+str(i)+'.png', bitmap_format='png')
                print(i)
                images = []