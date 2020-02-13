from matplotlib import animation, rc
import matplotlib.pyplot as plt
import numpy as np

class Visualizer:
    
    def __init__(self, points, colors = None, frames_per_points = 2, axes_name = ("X", "Y"),
        title = None, limits = None):
        """
            Visualizer
            
            Arguments:
                points {Matrix} -- 2D coordinates of data, each row is a point
                    Column 0 -> X position (optional)
                    Column 1 -> Y position
            
            Keyword Arguments:
                colors {List} -- List of colors for each point
                frames_per_points {int} -- Number of frames per points (default: {2})
                axes_name {(string, string)} -- Names to display
                title {string} -- Title
                limits {((int, int), (int, int))} -- Axis limit (default: {None - Automatic})
        """
        # Some non exhaustive checks
        assert len(points) > 0, "No animation needed"
        
        if len(points.shape) == 1:
            points = np.vstack([np.arange(len(points)), points]).T

        fig, self.ax = plt.subplots()
        self.plot = None
        self.frames_per_points = frames_per_points
        self.total_frames = frames_per_points * len(points)

        self.points = points
        self.title = title
        self.xlim, self.ylim = self._compute_limits_(points) if limits is None else limits
        self.xlabel, self.ylabel = axes_name
        self.colors = ["blue"] * len(points) if colors is None else colors

        self.animation = animation.FuncAnimation(fig, self._animate_, init_func = self._init_, frames = self.total_frames, interval = 20)
    
    def _init_(self):
        """
            Initializes the animation
        """
        self._clear_()
        self.ax.set_title(self.title)
        self.plot = self.ax.scatter(self.points[0, 0], self.points[0, 1], c = self.colors[0], alpha = 0.5)
        return (self.plot, )
    
    def _animate_(self, i):
        """
            Animates the gif
        """
        print("{:.2f} %".format(i / self.total_frames * 100), end = "\r")    
        if i % self.frames_per_points:
            i = i // self.frames_per_points
            self._clear_()
            self.plot = self.ax.plot(self.points[:i, 0], self.points[:i, 1], alpha = 0.5)
            self.plot = self.ax.scatter(self.points[i, 0], self.points[i, 1], c = self.colors[i], alpha = 0.5)
            self.ax.set_title(self.title)
        return (self.plot,)
    
    def _clear_(self):
        """
            Clears current ax
        """
        self.ax.clear()
        self.ax.set_xlim(self.xlim)
        self.ax.set_ylim(self.ylim)
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)
    
    def _compute_limits_(self, points, epsilon = 0.1):
        """
            Computes the limits of the figure
            
            Arguments:
                transformations {list of 2d matrices} -- Coordinates of points

            Returns:
                (xmin, xmax), (ylim, ymax)
        """
        # For memory efficiency (avoiding allocating agglomeration of all matrices)
        xmin, xmax = min(points[:, 0]), max(points[:, 0])
        ymin, ymax = min(points[:, 1]), max(points[:, 1])

        return (xmin - epsilon, xmax + epsilon), (ymin - epsilon, ymax + epsilon)

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
    

class TransformationVisualizer(Visualizer):

    def __init__(self, transformations, frames_per_transformation = 50, 
        frames_per_transition = 100, axes_name = ("", ""), titles = None, legend = False):
        """
            Visualizer
            
            Arguments:
                transformations {List of Matrix} -- 2D views of data, each element of the data is
                    num_rows * 2 or num_rows * 3 if classes is not None
                    Column 0 -> X position
                    Column 1 -> Y position

                    Column 2 -> Classes (must match classes dictionary)
            
            Keyword Arguments:
                frames_per_transformation {int} -- Number of frames per transformation (default: {100})
                frames_per_transition {int} -- Number of frames between transformation (default: {50})
                axes_name {(string, string)} -- Names to display
                titles {List string} -- List of titles to display
        """
        # Some non exhaustive checks
        assert len(transformations) > 0, "No animation needed"
        assert len(np.unique([t.shape for t in transformations])) == 2, "Dimensionality changes between transformations"

        fig, self.ax = plt.subplots()
        self.scatter = None
        self.frames_per_transformation, self.frames_per_transition = frames_per_transformation, frames_per_transition
        self.total_frames = (frames_per_transformation + frames_per_transition) * len(transformations)

        self.transformations = transformations
        self.titles = [str(i) for i in range(len(transformations))] if titles is None else titles
        self.current_transformation = 0
        self.xlim, self.ylim = self._compute_limits_(transformations)
        self.xlabel, self.ylabel = axes_name
        self.legend = legend

        self.animation = animation.FuncAnimation(fig, self._animate_, init_func = self._init_, frames = self.total_frames, interval = 20)

    def _init_(self):
        """
            Initializes the animation
        """
        self.current_transformation = 0
        self._clear_()
        self.ax.set_title(self.titles[self.current_transformation])
        self.scatter = self.ax.scatter(self.transformations[0][:,0], self.transformations[0][:,1], c = self._colors_(0), alpha = 0.5)
        if self.legend:
            self.ax.legend(*self.scatter.legend_elements(), bbox_to_anchor=(1.04,1), loc="upper left", title="Classes")
            plt.tight_layout()
        return (self.scatter, )
    
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

            title = "{} -> {}".format(self.titles[self.current_transformation], self.titles[next_transformation])
            num_after_t = i - (until_current + self.frames_per_transformation)
            ratio = (self.frames_per_transition - num_after_t) / self.frames_per_transition
            xs = ratio * current_xs + (1 - ratio) * next_xs
            ys = ratio * current_ys + (1 - ratio) * next_ys
        else:
            self.current_transformation = next_transformation
            title = self.titles[self.current_transformation]
            xs, ys = self.transformations[self.current_transformation][:, 0], \
                self.transformations[self.current_transformation][:, 1]
            
        
        self._clear_()
        self.scatter = self.ax.scatter(xs, ys, c = self._colors_(self.current_transformation), alpha = 0.5)
        self.ax.set_title(title)
        if self.legend:
            self.ax.legend(*self.scatter.legend_elements(), bbox_to_anchor=(1.04,1), loc="upper left", title="Classes")
            plt.tight_layout()
        return (self.scatter,)

    def _compute_limits_(self, transformations, epsilon = 0.1):
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

        return (xmin - epsilon, xmax + epsilon), (ymin - epsilon, ymax + epsilon)
    
    def _colors_(self, i):
        """
            Returns labels for the current transformation
            
            Arguments:
                i {int} -- Iteration
        """
        if self.legend:
            if self.transformations[i].shape[1] == 3:
                return self.transformations[i][:, 2]
            elif self.transformations[0].shape[1] == 3:
                return self.transformations[0][:, 2]
        return None