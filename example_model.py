# MIT License

# Copyright (c) 2019 Runway AI, Inc

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import random
from PIL import Image
import shutil
import os
import subprocess
from smartgrid import run_grid

resize_command_template = "convert workspace/input.png \
    -resize $(convert workspace/input.png -format '%[fx:{0}*int((w+1)/{0})]x%[fx:{0}*int((h+1)/{0})]!' info:) \
    workspace/input_sized.png"
tile_command_template = "convert workspace/input_sized.png +repage -crop {0} workspace/tile%04d.png"
montage_command_template = "montage workspace/tile????.png -geometry +2+2 -tile {0}x{0} workspace/grid.jpg"

use_imagemagick = False
def run_smartgrid(input_glob, output_path, model):
    run_grid(input_glob, None, None, 1.0,
        output_path, 2,
        30, 150, None, None, None,
        False, 0, None, False, None,
        "3+",
        model, None, None, False, "grid.jpg", use_imagemagick,
        0, False, None,
        None, None,
        1, False, False,
        False, False)


    # this obviously needs refactoring
    # run_grid(args.input_glob, args.left_image, args.right_image, args.left_right_scale,
    #          args.output_path, args.num_dimensions, 
    #          args.perplexity, args.learning_rate, width, height, args.aspect_ratio,
    #          args.drop_to_fit, args.fill_shade, args.vectors, args.do_prune, args.clip_range,
    #          args.subsampling,
    #          model, layer, args.pooling, args.do_crop, args.grid_file, args.use_imagemagick,
    #          args.grid_spacing, args.show_links, args.links_max_threshold,
    #          args.min_distance, args.max_distance,
    #          args.max_group_size, args.do_reload, args.do_tsne,
    #          args.do_reduce_hack, args.do_pca)

class ExampleModel():

    def __init__(self, options):
        random.seed(options['seed'])
        self.truncation = options['truncation']

    # Generate an image based on some text.
    def run_on_input(self, input_image, num_slices, model):
        print("HERE WE GO")
        shutil.rmtree('workspace', ignore_errors=True)
        os.mkdir('workspace')
        input_image.save("workspace/input.png")
        resize_command = resize_command_template.format(num_slices)
        tile_percent = "{:2.10f}%".format(100/num_slices)
        tile_command = tile_command_template.format(tile_percent)
        montage_command = montage_command_template.format(num_slices)
        outstr = str(subprocess.check_output(resize_command, shell=True, stderr=subprocess.STDOUT))
        outstr = outstr + str(subprocess.check_output(tile_command, shell=True, stderr=subprocess.STDOUT))

        if model == "none":
            os.system(montage_command)
        else:
            run_smartgrid("workspace/tile????.png", "workspace", model)
        # outstr = outstr + str(subprocess.check_output(montage_command, shell=True, stderr=subprocess.STDOUT))
        # outstr = outstr + str(subprocess.check_output("ls workspace", shell=True, stderr=subprocess.STDOUT))
        # os.system(resize_command)
        # os.system(tile_command)
        # print("WHAT ABOUT ", montage_command)
        # os.system(montage_command)
        tile1 = Image.open("workspace/grid.jpg").convert(mode='RGB')
        return {'image': tile1, 'info': outstr}

        # This is an example of how you could use some input from
        # @runway.setup(), like options['truncation'], later inside a
        # function called by @runway.command().
        # text = caption_text[0:self.truncation]

        # Return a red image if the input text is "red",
        # otherwise return a blue image.
        # if text == 'red':
        #     return Image.new('RGB', (512, 512), color = 'red')
        # else:
        #     return Image.new('RGB', (512, 512), color = 'blue')
        # return Image.new('RGB', (512, 512), color = 'blue')

