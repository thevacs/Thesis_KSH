"""
main training script
remember to set 'iteration_to_load' variable to 0 when train from scratch
"""
import lpdetect_model
from loss import loss
from keras.optimizers import Adam
from label_processing import DataProvider
from os.path import join
from time import time

if __name__ == '__main__':

    model = lpdetect_model.model_WPOD()

    training_dim = 208
    iterations = 300000
    batch_size = 32
    optimizer = Adam(lr=0.01)
    record_interval = 1000
    splice_train = True

    if splice_train:
        real_training_dim = training_dim * 2
    else:
        real_training_dim = training_dim

    training_data_folder = '/home/shaoheng/Documents/Thesis_KSH/training_data/CCPD_FR_total2333'
    saving_folder = '/home/shaoheng/Documents/Thesis_KSH/training_result/CCPD_FR_2333_splice_transferlearn'

    iteration_to_load = 0
    # comment this line if train from scratch
    # model.load_weights(join(saving_folder, 'Dim%dIt%dBsize%d.h5' % (training_dim, iteration_to_load, batch_size)))

    # if use transfer learning
    model.load_weights('/home/shaoheng/Documents/Thesis_KSH/training_result/CCPD_FR_2333_splice_transferlearn/init_Dim208It79000Bsize64.h5')

    model.compile(loss=loss, optimizer=optimizer)

    data_provider = DataProvider(training_data_folder, batch_size, training_dim, 16,
                                 CCPD_origin=False, splice_train=splice_train)
    data_provider.start_loading()

    start_time = time()

    for iteration in range(iterations):
        train_x, train_y = data_provider.get_batch()

        print 'start training on mini batch'
        training_loss = model.train_on_batch(train_x, train_y)

        total_iteration = iteration_to_load + (iteration + 1)
        print 'iteration: %d, training loss:' % total_iteration, training_loss

        # save model
        if (iteration + 1) % record_interval == 0:

            time_used = time() - start_time
            start_time = time()

            print 'save weight to', saving_folder
            model.save_weights(join(saving_folder, 'Dim%dIt%dBsize%d.h5' %
                                    (real_training_dim, total_iteration, batch_size)))

            with open(join(saving_folder, 'record.txt'), 'a+') as f:
                f.write('iteration %d to %d, time spent: %.2f sec, loss: %.2f\n' %
                        (iteration + 1 - record_interval, iteration + 1, time_used, training_loss))

    data_provider.stop_loading()


