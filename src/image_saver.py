import os
import matplotlib.pyplot as plt
import numpy as np
from keras.callbacks import LambdaCallback

# global for closure, gross
current_epoch = 0

def image_saver_callback(model, directory, interval=100, cmap='gray', render_videos=False):
    
    def save_image(weights, batch, layer_name, i):
        global current_epoch
        weight = str(i + 1).zfill(2)
        epoch = str(current_epoch).zfill(3)
        fold = os.path.join(directory, 'epoch_{}-layer_{}-weights_{}'.format(epoch, layer_name, weight))
        if not os.path.isdir(fold):
            os.makedirs(fold)
        name = os.path.join('{}'.format(fold),
                            '{}_{}x{}.png'.format(str(batch).zfill(9), 
                                                  weights.shape[0], weights.shape[1]))
        plt.imsave(name, weights, cmap=cmap)
    
    def save_weight_images(batch, logs):
        if batch % interval == 0:
            for layer in model.layers:
                if len(layer.get_weights()) > 0:
                    for i, weights in enumerate(layer.get_weights()):
                        if len(weights.shape) < 2:
                            weights = np.expand_dims(weights, axis=0)
                        save_image(weights, batch, layer.name, i)
    
    def on_epoch_begin(epoch, logs):
        global current_epoch
        current_epoch = epoch

    def on_train_end(logs):
        src = os.path.dirname(os.path.abspath(__file__))
        cmd = os.path.join(src, '..', 'bin', 'create_image_sequence.sh')
        print(os.system('{} {}'.format(cmd, directory)))

    kwargs = dict()
    kwargs['on_batch_begin'] = save_weight_images
    kwargs['on_epoch_begin'] = on_epoch_begin
    if render_videos:
        kwargs['on_train_end'] = on_train_end

    return LambdaCallback(**kwargs)
