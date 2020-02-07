from matplotlib import animation, rc
import matplotlib.pyplot as plt
import numpy as np

class TransformationVisualizer:

    def __init__(self, transformations, classes = None, colors = None, 
        frames_per_transformation = 10, frames_per_transition = 100, axes_name = ("X", "Y")):
        """
            Visualizer
            
            Arguments:
                transformations {List of Matrix} -- 2D views of data, each element of the data is
                    num_rows * 2 or num_rows * 3 if classes is not None
                    Column 0 -> X position
                    Column 1 -> Y position

                    Column 2 -> Classes (must match classes dictionary)
            
            Keyword Arguments:
                classes {Dict} -- Dictionary of classes associated a name to the classes present in 
                    transformations matrix (default: {None: No classes})
                colors {Dict} -- Dictionary of colors to associated to each classes 
                    (same keys than classes)
                frames_per_transformation {int} -- Number of frames per transformation (default: {10})
                frames_per_transition {int} -- Number of frames between transformation (default: {10})
                axes_name {(string, string)} -- Names to display
        """
        # Some non exhaustive checks
        assert len(transformations) > 0, "No animation needed"
        assert len(np.unique([t.shape for t in transformations])) == 2, "Dimensionality changes between transformations"

        fig, self.ax = plt.subplots()
        self.scatter = None
        self.frames_per_transformation, self.frames_per_transition = frames_per_transformation, frames_per_transition
        self.total_frames = (frames_per_transformation + frames_per_transition) * len(transformations)
        self.animation = animation.FuncAnimation(fig, self._animate_, init_func = self._init_, frames = self.total_frames, interval = 20)

        self.transformations = transformations
        self.current_transformation = 0
        self.xlim, self.ylim = self._compute_limits_(transformations)
        self.xlabel, self.ylabel = axes_name
        self.colors = colors if colors is None else [colors[p] for p in self.transformations[0][:, 2]]

    def _init_(self):
        """
            Initializes the animation
        """
        self.current_transformation = 0
        self._clear_()
        self.scatter = self.ax.scatter(self.transformations[0][:,0], self.transformations[0][:,1], c = self.colors, alpha = 0.5)
        return (self.scatter, )

    def _clear_(self):
        """
            Clears current ax
        """
        self.ax.clear()
        self.ax.set_xlim(self.xlim)
        self.ax.set_ylim(self.ylim)
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)

    def _animate_(self, i):
        """
            Animates the gif
        """
        print("{:.2f} %".format(i / self.total_frames * 100), end = "\r")

        until_current = self.current_transformation * (self.frames_per_transformation + self.frames_per_transition)
        next_transformation = (self.current_transformation + 1) % len(self.transformations)
        if i < until_current + self.frames_per_transformation:
            return (self.scatter,)
        elif i < until_current + self.frames_per_transformation + self.frames_per_transition:
            current_xs, current_ys = self.transformations[self.current_transformation][:, 0], \
                self.transformations[self.current_transformation][:, 1]
            next_xs, next_ys = self.transformations[next_transformation][:, 0], \
                self.transformations[next_transformation][:, 1]

            num_after_t = i - (until_current + self.frames_per_transformation)
            ratio = (self.frames_per_transition - num_after_t) / self.frames_per_transition
            xs = ratio * current_xs + (1 - ratio) * next_xs
            ys = ratio * current_ys + (1 - ratio) * next_ys
        else:
            self.current_transformation = next_transformation
            xs, ys = self.transformations[self.current_transformation][:, 0], \
                self.transformations[self.current_transformation][:, 1]
        
        self._clear_()
        self.scatter = self.ax.scatter(xs, ys, c = self.colors, alpha = 0.5)

        return (self.scatter,)

    def _compute_limits_(self, transformations):
        """
            Computes the limits of the figure
            
            Arguments:
                transformations {list of 2d matrices} -- Coordinates of points

            Returns:
                (xmin, xmax), (ylim, ymax)
        """
        # For memory efficiency (avoiding allocating agglomeration of all matrices)
        xmin, xmax = min([min(t[:, 0]) for t in transformations]), max([max(t[:, 0]) for t in transformations])
        ymin, ymax = min([min(t[:, 1]) for t in transformations]), max([max(t[:, 1]) for t in transformations])

        return (xmin, xmax), (ymin, ymax)

    def save_gif(self, gifname, fps = 60):
        """
        Saves animation in gif format
        
            Arguments:
                gifname {string} -- gif name and path to save animation
            
            Keyword Arguments:
                fps {int} -- Number of frames per second (default: {60})
        """
        self.animation.save(gifname, writer = "imagemagick", fps = fps)

    def jupyter_visualize(self):
        """
            Visualizes in a jupter notebook
        """
        from IPython.display import HTML
        return HTML(self.animation.to_jshtml())