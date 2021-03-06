import tensorflow as tf


class ActorCritic(tf.keras.Model):
    '''
    len(convolution_layers) = number of convolution layers, 
    convolution_layers[i][0] = kernel shape (square)
    covolution_layers[i][1] = # of kernels per layer,
    covolution_layers[i][2] = stride,
    covolution_layers[i][3] = max_pool stride and kernel size,

    len(fully_connected_layers) = number of hidden neural layers, 
    fully_connected_layers[i] = # of neurons per layer
    '''

    def __init__(self, name, numberOutputs, convolutionLayers, denseLayers, lstmUnits, training):
        super(ActorCritic, self).__init__(name=name)
        self.training = training

        # Convolutional Layers
        self.convolutionLayers = []
        self.poolingLayers = []
        i = 0
        for convLayer in convolutionLayers:
            self.convolutionLayers.append(tf.keras.layers.Conv2D(
                convLayer[1], convLayer[0], padding='same', activation='relu'
            ))
            self.poolingLayers.append(
                tf.keras.layers.MaxPool2D(padding='same'))
            i += 1

        # Flattening Layer
        self.flatten = tf.keras.layers.Flatten()

        # LSTM Layer
        self.lstmCell = tf.keras.layers.LSTMCell(lstmUnits)
        self.lstmRNN = tf.keras.layers.RNN(self.lstmCell, return_state=True)

        # Dense Layers
        self.denseLayers = []
        i = 0
        for denseLayer in denseLayers:
            self.denseLayers.append(tf.keras.layers.Dense(
                denseLayer, activation='relu'))
            i += 1

        # Actor Layers
        self.actor = tf.keras.layers.Dense(
            numberOutputs, activation='linear')

        # Critic Layer
        self.critic = tf.keras.layers.Dense(1, activation='linear')

    def call(self, inputTensor, state):
        x = self.convolutionalLayerCall(inputTensor)
        x, state = self.lstmLayerCall(x, state)
        actorValues, criticValues = self.outputLayerCall(x)
        return actorValues, criticValues, state

    def warmupCall(self, inputTensor):
        x = self.convolutionalLayerCall(inputTensor)
        x = tf.reshape(x, [1, x.shape[0] ,x.shape[1]]) #REVER!!!!
        '''
        # x.shape => (batch, time, features)
        '''
        x, *state = self.lstmRNN(x)
        prediction = self.outputLayerCall(x)
        return prediction, state

    def convolutionalLayerCall(self, inputTensor):
        x = inputTensor
        for conv, pool in zip(self.convolutionLayers, self.poolingLayers):
            x = conv(x)
            x = pool(x)
        x = self.flatten(x)
        return x

    def lstmLayerCall(self, inputTensor, state):
        x, state = self.lstmCell(
            inputTensor, states=state, training=self.training)
        return x, state
 
    def outputLayerCall(self, inputTensor):
        x = inputTensor
        for dense in self.denseLayers:
            x = dense(x)
        actorValues = self.actor(x)
        criticValues = self.critic(x)
        return actorValues, criticValues
