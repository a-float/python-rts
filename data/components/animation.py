class Animation:
    def __init__(self, frames, fps):
        self.frames = frames
        self.fps = fps
        self.frame = 0
        self.timer = None

    def get_next_frame(self, now):

        if not self.timer:
            self.timer = now
        if now - self.timer > 1000.0 / self.fps:
            self.frame = (self.frame + 1) % len(self.frames)
            self.timer = now
        return self.frames[self.frame]

