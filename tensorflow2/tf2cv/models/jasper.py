"""
    Jasper/DR for ASR, implemented in TensorFlow.
    Original paper: 'Jasper: An End-to-End Convolutional Neural Acoustic Model,' https://arxiv.org/abs/1904.03288.
"""

__all__ = ['Jasper', 'jasper5x3', 'jasper10x4', 'jasper10x5', 'get_jasper']

import os
import tensorflow as tf
import tensorflow.keras.layers as nn
from .common import get_activation_layer, Conv1d, BatchNorm, DualPathSequential, DualPathParallelConcurent,\
    is_channels_first


def conv1d1(in_channels,
            out_channels,
            strides=1,
            groups=1,
            use_bias=False,
            data_format="channels_last",
            **kwargs):
    """
    1-dim kernel version of the 1D convolution layer.

    Parameters:
    ----------
    in_channels : int
        Number of input channels.
    out_channels : int
        Number of output channels.
    strides : int, default 1
        Strides of the convolution.
    groups : int, default 1
        Number of groups.
    use_bias : bool, default False
        Whether the layer uses a bias vector.
    data_format : str, default 'channels_last'
        The ordering of the dimensions in tensors.
    """
    return Conv1d(
        in_channels=in_channels,
        out_channels=out_channels,
        kernel_size=1,
        strides=strides,
        groups=groups,
        use_bias=use_bias,
        data_format=data_format,
        **kwargs)


class MaskConv1d(Conv1d):
    """
    Masked 1D convolution block.

    Parameters:
    ----------
    in_channels : int
        Number of input channels.
    out_channels : int
        Number of output channels.
    kernel_size : int or tuple/list of 1 int
        Convolution window size.
    strides : int or tuple/list of 1 int
        Strides of the convolution.
    padding : int or tuple/list of 1 int, default 0
        Padding value for convolution layer.
    dilation : int or tuple/list of 1 int, default 1
        Dilation value for convolution layer.
    groups : int, default 1
        Number of groups.
    use_bias : bool, default False
        Whether the layer uses a bias vector.
    use_mask : bool, default True
        Whether to use mask.
    data_format : str, default 'channels_last'
        The ordering of the dimensions in tensors.
    """
    def __init__(self,
                 in_channels,
                 out_channels,
                 kernel_size,
                 strides,
                 padding=0,
                 dilation=1,
                 groups=1,
                 use_bias=False,
                 use_mask=True,
                 data_format="channels_last",
                 **kwargs):
        super(MaskConv1d, self).__init__(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            strides=strides,
            padding=padding,
            dilation=dilation,
            groups=groups,
            use_bias=use_bias,
            data_format=data_format,
            **kwargs)
        self.use_mask = use_mask
        self.data_format = data_format
        if self.use_mask:
            self.kernel_size = kernel_size[0] if isinstance(kernel_size, (list, tuple)) else kernel_size
            self.strides = strides[0] if isinstance(strides, (list, tuple)) else strides
            self.padding = padding[0] if isinstance(padding, (list, tuple)) else padding
            self.dilation = dilation[0] if isinstance(dilation, (list, tuple)) else dilation

    def call(self, x, x_len):
        if self.use_mask:
            if is_channels_first(self.data_format):
                max_len = x.shape[2]
                mask = tf.expand_dims(tf.cast(tf.linspace(0, max_len - 1, max_len), tf.int64), 0) <\
                       tf.expand_dims(x_len, -1)
                mask = tf.broadcast_to(tf.expand_dims(mask, 1), x.shape)
                x = tf.where(mask, x, tf.zeros(x.shape))
            else:
                max_len = x.shape[1]
                mask = tf.expand_dims(tf.cast(tf.linspace(0, max_len - 1, max_len), tf.int64), 0) <\
                       tf.expand_dims(x_len, -1)
                mask = tf.broadcast_to(tf.expand_dims(mask, -1), x.shape)
                x = tf.where(mask, x, tf.zeros(x.shape))
            x_len = (x_len + 2 * self.padding - self.dilation * (self.kernel_size - 1) - 1) // self.strides + 1
        x = super(MaskConv1d, self).call(x)
        return x, x_len


def mask_conv1d1(in_channels,
                 out_channels,
                 strides=1,
                 groups=1,
                 use_bias=False,
                 data_format="channels_last",
                 **kwargs):
    """
    Masked 1-dim kernel version of the 1D convolution layer.

    Parameters:
    ----------
    in_channels : int
        Number of input channels.
    out_channels : int
        Number of output channels.
    strides : int, default 1
        Strides of the convolution.
    groups : int, default 1
        Number of groups.
    use_bias : bool, default False
        Whether the layer uses a bias vector.
    data_format : str, default 'channels_last'
        The ordering of the dimensions in tensors.
    """
    return MaskConv1d(
        in_channels=in_channels,
        out_channels=out_channels,
        kernel_size=1,
        strides=strides,
        groups=groups,
        use_bias=use_bias,
        data_format=data_format,
        **kwargs)


class MaskConvBlock1d(nn.Layer):
    """
    Masked 1D convolution block with batch normalization, activation, and dropout.

    Parameters:
    ----------
    in_channels : int
        Number of input channels.
    out_channels : int
        Number of output channels.
    kernel_size : int
        Convolution window size.
    strides : int
        Strides of the convolution.
    padding : int
        Padding value for convolution layer.
    dilation : int, default 1
        Dilation value for convolution layer.
    groups : int, default 1
        Number of groups.
    use_bias : bool, default False
        Whether the layer uses a bias vector.
    use_bn : bool, default True
        Whether to use BatchNorm layer.
    bn_eps : float, default 1e-5
        Small float added to variance in Batch norm.
    activation : function or str or None, default 'relu'
        Activation function or name of activation function.
    dropout_rate : float, default 0.0
        Parameter of Dropout layer. Faction of the input units to drop.
    data_format : str, default 'channels_last'
        The ordering of the dimensions in tensors.
    """
    def __init__(self,
                 in_channels,
                 out_channels,
                 kernel_size,
                 strides,
                 padding,
                 dilation=1,
                 groups=1,
                 use_bias=False,
                 use_bn=True,
                 bn_eps=1e-5,
                 activation="relu",
                 dropout_rate=0.0,
                 data_format="channels_last",
                 **kwargs):
        super(MaskConvBlock1d, self).__init__(**kwargs)
        self.activate = (activation is not None)
        self.use_bn = use_bn
        self.use_dropout = (dropout_rate != 0.0)

        self.conv = MaskConv1d(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            strides=strides,
            padding=padding,
            dilation=dilation,
            groups=groups,
            use_bias=use_bias,
            data_format=data_format,
            name="conv")
        if self.use_bn:
            self.bn = BatchNorm(
                epsilon=bn_eps,
                data_format=data_format,
                name="bn")
        if self.activate:
            self.activ = get_activation_layer(activation, name="activ")
        if self.use_dropout:
            self.dropout = nn.Dropout(
                rate=dropout_rate,
                name="dropout")

    def call(self, x, x_len, training=None):
        x, x_len = self.conv(x, x_len)
        if self.use_bn:
            x = self.bn(x, training=training)
        if self.activate:
            x = self.activ(x)
        if self.use_dropout:
            x = self.dropout(x, training=training)
        return x, x_len


def mask_conv1d1_block(in_channels,
                       out_channels,
                       strides=1,
                       padding=0,
                       data_format="channels_last",
                       **kwargs):
    """
    1-dim kernel version of the masked 1D convolution block.

    Parameters:
    ----------
    in_channels : int
        Number of input channels.
    out_channels : int
        Number of output channels.
    strides : int, default 1
        Strides of the convolution.
    padding : int, default 0
        Padding value for convolution layer.
    data_format : str, default 'channels_last'
        The ordering of the dimensions in tensors.
    """
    return MaskConvBlock1d(
        in_channels=in_channels,
        out_channels=out_channels,
        kernel_size=1,
        strides=strides,
        padding=padding,
        data_format=data_format,
        **kwargs)


class ChannelShuffle1d(nn.Layer):
    """
    1D version of the channel shuffle layer.

    Parameters:
    ----------
    channels : int
        Number of channels.
    groups : int
        Number of groups.
    data_format : str, default 'channels_last'
        The ordering of the dimensions in tensors.
    """
    def __init__(self,
                 channels,
                 groups,
                 data_format="channels_last",
                 **kwargs):
        super(ChannelShuffle1d, self).__init__(**kwargs)
        assert (channels % groups == 0)
        self.groups = groups
        self.data_format = data_format

    def call(self, x, training=None):
        x_shape = x.get_shape().as_list()
        if is_channels_first(self.data_format):
            channels = x_shape[1]
            seq_len = x_shape[2]
        else:
            seq_len = x_shape[1]
            channels = x_shape[2]

        assert (channels % self.groups == 0)
        channels_per_group = channels // self.groups

        if is_channels_first(self.data_format):
            x = tf.reshape(x, shape=(-1, self.groups, channels_per_group, seq_len))
            x = tf.transpose(x, perm=(0, 2, 1, 3))
            x = tf.reshape(x, shape=(-1, channels, seq_len))
        else:
            x = tf.reshape(x, shape=(-1, seq_len, self.groups, channels_per_group))
            x = tf.transpose(x, perm=(0, 1, 3, 2))
            x = tf.reshape(x, shape=(-1, seq_len, channels))
        return x

    def __repr__(self):
        s = "{name}(groups={groups})"
        return s.format(
            name=self.__class__.__name__,
            groups=self.groups)


class DwsConvBlock1d(nn.Layer):
    """
    Depthwise version of the 1D standard convolution block with batch normalization, activation, dropout, and channel
    shuffle.

    Parameters:
    ----------
    in_channels : int
        Number of input channels.
    out_channels : int
        Number of output channels.
    kernel_size : int
        Convolution window size.
    strides : int
        Strides of the convolution.
    padding : int
        Padding value for convolution layer.
    dilation : int, default 1
        Dilation value for convolution layer.
    groups : int, default 1
        Number of groups.
    use_bias : bool, default False
        Whether the layer uses a bias vector.
    use_bn : bool, default True
        Whether to use BatchNorm layer.
    bn_eps : float, default 1e-5
        Small float added to variance in Batch norm.
    activation : function or str or None, default 'relu'
        Activation function or name of activation function.
    dropout_rate : float, default 0.0
        Parameter of Dropout layer. Faction of the input units to drop.
    data_format : str, default 'channels_last'
        The ordering of the dimensions in tensors.
    """
    def __init__(self,
                 in_channels,
                 out_channels,
                 kernel_size,
                 strides,
                 padding,
                 dilation=1,
                 groups=1,
                 use_bias=False,
                 use_bn=True,
                 bn_eps=1e-5,
                 activation="relu",
                 dropout_rate=0.0,
                 data_format="channels_last",
                 **kwargs):
        super(DwsConvBlock1d, self).__init__(**kwargs)
        self.activate = (activation is not None)
        self.use_bn = use_bn
        self.use_dropout = (dropout_rate != 0.0)
        self.use_channel_shuffle = (groups > 1)

        self.dw_conv = MaskConv1d(
            in_channels=in_channels,
            out_channels=in_channels,
            kernel_size=kernel_size,
            strides=strides,
            padding=padding,
            dilation=dilation,
            groups=in_channels,
            use_bias=use_bias,
            data_format=data_format,
            name="dw_conv")
        self.pw_conv = mask_conv1d1(
            in_channels=in_channels,
            out_channels=out_channels,
            groups=groups,
            use_bias=use_bias,
            data_format=data_format,
            name="pw_conv")
        if self.use_channel_shuffle:
            self.shuffle = ChannelShuffle1d(
                channels=out_channels,
                groups=groups,
                data_format=data_format,
                name="shuffle")
        if self.use_bn:
            self.bn = BatchNorm(
                epsilon=bn_eps,
                data_format=data_format,
                name="bn")
        if self.activate:
            self.activ = get_activation_layer(activation, name="activ")
        if self.use_dropout:
            self.dropout = nn.Dropout(
                rate=dropout_rate,
                name="dropout")

    def call(self, x, x_len, training=None):
        x, x_len = self.dw_conv(x, x_len)
        x, x_len = self.pw_conv(x, x_len)
        if self.use_channel_shuffle:
            x = self.shuffle(x)
        if self.use_bn:
            x = self.bn(x, training=training)
        if self.activate:
            x = self.activ(x)
        if self.use_dropout:
            x = self.dropout(x, training=training)
        return x, x_len


class JasperUnit(nn.Layer):
    """
    Jasper unit with residual connection.

    Parameters:
    ----------
    in_channels : int or list of int
        Number of input channels.
    out_channels : int
        Number of output channels.
    kernel_size : int
        Convolution window size.
    bn_eps : float
        Small float added to variance in Batch norm.
    dropout_rate : float
        Parameter of Dropout layer. Faction of the input units to drop.
    repeat : int
        Count of body convolution blocks.
    use_dw : bool
        Whether to use depthwise block.
    use_dr : bool
        Whether to use dense residual scheme.
    data_format : str, default 'channels_last'
        The ordering of the dimensions in tensors.
    """
    def __init__(self,
                 in_channels,
                 out_channels,
                 kernel_size,
                 bn_eps,
                 dropout_rate,
                 repeat,
                 use_dw,
                 use_dr,
                 data_format="channels_last",
                 **kwargs):
        super(JasperUnit, self).__init__(**kwargs)
        self.use_dropout = (dropout_rate != 0.0)
        self.use_dr = use_dr
        block_class = DwsConvBlock1d if use_dw else MaskConvBlock1d

        if self.use_dr:
            self.identity_block = DualPathParallelConcurent(name="identity_block")
            for i, dense_in_channels_i in enumerate(in_channels):
                self.identity_block.add(mask_conv1d1_block(
                    in_channels=dense_in_channels_i,
                    out_channels=out_channels,
                    bn_eps=bn_eps,
                    dropout_rate=0.0,
                    activation=None,
                    data_format=data_format,
                    name="block{}".format(i + 1)))
            in_channels = in_channels[-1]
        else:
            self.identity_block = mask_conv1d1_block(
                in_channels=in_channels,
                out_channels=out_channels,
                bn_eps=bn_eps,
                dropout_rate=0.0,
                activation=None,
                data_format=data_format,
                name="identity_block")

        self.body = DualPathSequential(name="body")
        for i in range(repeat):
            activation = "relu" if i < repeat - 1 else None
            dropout_rate_i = dropout_rate if i < repeat - 1 else 0.0
            self.body.add(block_class(
                in_channels=in_channels,
                out_channels=out_channels,
                kernel_size=kernel_size,
                strides=1,
                padding=(kernel_size // 2),
                bn_eps=bn_eps,
                dropout_rate=dropout_rate_i,
                activation=activation,
                data_format=data_format,
                name="block{}".format(i + 1)))
            in_channels = out_channels

        self.activ = nn.ReLU()
        if self.use_dropout:
            self.dropout = nn.Dropout(
                rate=dropout_rate,
                name="dropout")

    def call(self, x, x_len, training=None):
        if self.use_dr:
            x_len, y, y_len = x_len if type(x_len) is tuple else (x_len, None, None)
            y = [x] if y is None else y + [x]
            y_len = [x_len] if y_len is None else y_len + [x_len]
            identity, _ = self.identity_block(y, y_len, training=training)
            identity = tf.stack(identity, axis=1)
            identity = tf.math.reduce_sum(identity, axis=1)
        else:
            identity, _ = self.identity_block(x, x_len, training=training)

        x, x_len = self.body(x, x_len, training=training)
        x = x + identity
        x = self.activ(x)
        if self.use_dropout:
            x = self.dropout(x, training=training)

        if self.use_dr:
            return x, (x_len, y, y_len)
        else:
            return x, x_len


class JasperFinalBlock(nn.Layer):
    """
    Jasper specific final block.

    Parameters:
    ----------
    in_channels : int
        Number of input channels.
    channels : list of int
        Number of output channels for each block.
    kernel_sizes : list of int
        Kernel sizes for each block.
    bn_eps : float
        Small float added to variance in Batch norm.
    dropout_rates : list of int
        Dropout rates for each block.
    use_dw : bool
        Whether to use depthwise block.
    use_dr : bool
        Whether to use dense residual scheme.
    data_format : str, default 'channels_last'
        The ordering of the dimensions in tensors.
    """
    def __init__(self,
                 in_channels,
                 channels,
                 kernel_sizes,
                 bn_eps,
                 dropout_rates,
                 use_dw,
                 use_dr,
                 data_format="channels_last",
                 **kwargs):
        super(JasperFinalBlock, self).__init__(**kwargs)
        self.use_dr = use_dr
        conv1_class = DwsConvBlock1d if use_dw else MaskConvBlock1d

        self.conv1 = conv1_class(
            in_channels=in_channels,
            out_channels=channels[-2],
            kernel_size=kernel_sizes[-2],
            strides=1,
            padding=(2 * kernel_sizes[-2] // 2 - 1),
            dilation=2,
            bn_eps=bn_eps,
            dropout_rate=dropout_rates[-2],
            data_format=data_format,
            name="conv1")
        self.conv2 = MaskConvBlock1d(
            in_channels=channels[-2],
            out_channels=channels[-1],
            kernel_size=kernel_sizes[-1],
            strides=1,
            padding=(kernel_sizes[-1] // 2),
            bn_eps=bn_eps,
            dropout_rate=dropout_rates[-1],
            data_format=data_format,
            name="conv2")

    def call(self, x, x_len, training=None):
        if self.use_dr:
            x_len = x_len[0]
        x, x_len = self.conv1(x, x_len, training=training)
        x, x_len = self.conv2(x, x_len, training=training)
        return x, x_len


class Jasper(tf.keras.Model):
    """
    Jasper/DR/QuartzNet model from 'Jasper: An End-to-End Convolutional Neural Acoustic Model,'
    https://arxiv.org/abs/1904.03288.

    Parameters:
    ----------
    channels : list of int
        Number of output channels for each unit and initial/final block.
    kernel_sizes : list of int
        Kernel sizes for each unit and initial/final block.
    bn_eps : float
        Small float added to variance in Batch norm.
    dropout_rates : list of int
        Dropout rates for each unit and initial/final block.
    repeat : int
        Count of body convolution blocks.
    use_dw : bool
        Whether to use depthwise block.
    use_dr : bool
        Whether to use dense residual scheme.
    vocabulary : list of str or None, default None
        Vocabulary of the dataset.
    in_channels : int, default 64
        Number of input channels (audio features).
    classes : int, default 29
        Number of classification classes (number of graphemes).
    data_format : str, default 'channels_last'
        The ordering of the dimensions in tensors.
    """
    def __init__(self,
                 channels,
                 kernel_sizes,
                 bn_eps,
                 dropout_rates,
                 repeat,
                 use_dw,
                 use_dr,
                 vocabulary=None,
                 in_channels=64,
                 classes=29,
                 data_format="channels_last",
                 **kwargs):
        super(Jasper, self).__init__(**kwargs)
        self.in_size = in_channels
        self.in_channels = in_channels
        self.classes = classes
        self.vocabulary = vocabulary
        self.data_format = data_format

        self.features = DualPathSequential(name="features")
        init_block_class = DwsConvBlock1d if use_dw else MaskConvBlock1d
        self.features.add(init_block_class(
            in_channels=in_channels,
            out_channels=channels[0],
            kernel_size=kernel_sizes[0],
            strides=2,
            padding=(kernel_sizes[0] // 2),
            bn_eps=bn_eps,
            dropout_rate=dropout_rates[0],
            data_format=data_format,
            name="init_block"))
        in_channels = channels[0]
        in_channels_list = []
        for i, (out_channels, kernel_size, dropout_rate) in \
                enumerate(zip(channels[1:-2], kernel_sizes[1:-2], dropout_rates[1:-2])):
            in_channels_list += [in_channels]
            self.features.add(JasperUnit(
                in_channels=(in_channels_list if use_dr else in_channels),
                out_channels=out_channels,
                kernel_size=kernel_size,
                bn_eps=bn_eps,
                dropout_rate=dropout_rate,
                repeat=repeat,
                use_dw=use_dw,
                use_dr=use_dr,
                data_format=data_format,
                name="unit{}".format(i + 1)))
            in_channels = out_channels
        self.features.add(JasperFinalBlock(
            in_channels=in_channels,
            channels=channels,
            kernel_sizes=kernel_sizes,
            bn_eps=bn_eps,
            dropout_rates=dropout_rates,
            use_dw=use_dw,
            use_dr=use_dr,
            data_format=data_format,
            name="final_block"))
        in_channels = channels[-1]

        self.output1 = conv1d1(
            in_channels=in_channels,
            out_channels=classes,
            use_bias=True,
            data_format=data_format,
            name="output1")

    def call(self, x, x_len, training=None):
        x, x_len = self.features(x, x_len, training=training)
        x = self.output1(x)
        return x, x_len


def get_jasper(version,
               use_dw=False,
               use_dr=False,
               bn_eps=1e-3,
               vocabulary=None,
               model_name=None,
               pretrained=False,
               root=os.path.join("~", ".tensorflow", "models"),
               **kwargs):
    """
    Create Jasper/DR/QuartzNet model with specific parameters.

    Parameters:
    ----------
    version : tuple of str
        Model type and configuration.
    use_dw : bool, default False
        Whether to use depthwise block.
    use_dr : bool, default False
        Whether to use dense residual scheme.
    bn_eps : float, default 1e-3
        Small float added to variance in Batch norm.
    vocabulary : list of str or None, default None
        Vocabulary of the dataset.
    model_name : str or None, default None
        Model name for loading pretrained model.
    pretrained : bool, default False
        Whether to load the pretrained weights for model.
    root : str, default '~/.tensorflow/models'
        Location for keeping the model parameters.
    """
    import numpy as np

    blocks, repeat = tuple(map(int, version[1].split("x")))
    main_stage_repeat = blocks // 5

    model_type = version[0]
    if model_type == "jasper":
        channels_per_stage = [256, 256, 384, 512, 640, 768, 896, 1024]
        kernel_sizes_per_stage = [11, 11, 13, 17, 21, 25, 29, 1]
        dropout_rates_per_stage = [0.2, 0.2, 0.2, 0.2, 0.3, 0.3, 0.4, 0.4]
    elif model_type == "quartznet":
        channels_per_stage = [256, 256, 256, 512, 512, 512, 512, 1024]
        kernel_sizes_per_stage = [33, 33, 39, 51, 63, 75, 87, 1]
        dropout_rates_per_stage = [0.0] * 8
    else:
        raise ValueError("Unsupported Jasper family model type: {}".format(model_type))

    stage_repeat = np.full((8,), 1)
    stage_repeat[1:-2] *= main_stage_repeat
    channels = sum([[a] * r for (a, r) in zip(channels_per_stage, stage_repeat)], [])
    kernel_sizes = sum([[a] * r for (a, r) in zip(kernel_sizes_per_stage, stage_repeat)], [])
    dropout_rates = sum([[a] * r for (a, r) in zip(dropout_rates_per_stage, stage_repeat)], [])

    net = Jasper(
        channels=channels,
        kernel_sizes=kernel_sizes,
        bn_eps=bn_eps,
        dropout_rates=dropout_rates,
        repeat=repeat,
        use_dw=use_dw,
        use_dr=use_dr,
        vocabulary=vocabulary,
        **kwargs)

    if pretrained:
        if (model_name is None) or (not model_name):
            raise ValueError("Parameter `model_name` should be properly initialized for loading pretrained model.")
        from .model_store import get_model_file
        in_channels = kwargs["in_channels"] if ("in_channels" in kwargs) else 3
        input_shape = (1,) + (in_channels,) + net.in_size if net.data_format == "channels_first" else\
            (1,) + net.in_size + (in_channels,)
        net.build(input_shape=input_shape)
        net.load_weights(
            filepath=get_model_file(
                model_name=model_name,
                local_model_store_dir_path=root))

    return net


def jasper5x3(**kwargs):
    """
    Jasper 5x3 model from 'Jasper: An End-to-End Convolutional Neural Acoustic Model,'
    https://arxiv.org/abs/1904.03288.

    Parameters:
    ----------
    pretrained : bool, default False
        Whether to load the pretrained weights for model.
    root : str, default '~/.tensorflow/models'
        Location for keeping the model parameters.
    """
    return get_jasper(version=("jasper", "5x3"), model_name="jasper5x3", **kwargs)


def jasper10x4(**kwargs):
    """
    Jasper 10x4 model from 'Jasper: An End-to-End Convolutional Neural Acoustic Model,'
    https://arxiv.org/abs/1904.03288.

    Parameters:
    ----------
    pretrained : bool, default False
        Whether to load the pretrained weights for model.
    root : str, default '~/.tensorflow/models'
        Location for keeping the model parameters.
    """
    return get_jasper(version=("jasper", "10x4"), model_name="jasper10x4", **kwargs)


def jasper10x5(**kwargs):
    """
    Jasper 10x5 model from 'Jasper: An End-to-End Convolutional Neural Acoustic Model,'
    https://arxiv.org/abs/1904.03288.

    Parameters:
    ----------
    pretrained : bool, default False
        Whether to load the pretrained weights for model.
    root : str, default '~/.tensorflow/models'
        Location for keeping the model parameters.
    """
    return get_jasper(version=("jasper", "10x5"), model_name="jasper10x5", **kwargs)


def _test():
    import numpy as np
    import tensorflow.keras.backend as K

    data_format = "channels_last"
    # data_format = "channels_first"
    pretrained = False
    audio_features = 64
    classes = 29

    models = [
        jasper5x3,
        jasper10x4,
        jasper10x5,
    ]

    for model in models:

        net = model(
            in_channels=audio_features,
            classes=classes,
            pretrained=pretrained,
            data_format=data_format)

        batch = 3
        seq_len = np.random.randint(60, 150, batch)
        seq_len_max = seq_len.max() + 2
        x = tf.random.normal((batch, audio_features, seq_len_max) if is_channels_first(data_format) else
                             (batch, seq_len_max, audio_features))
        x_len = tf.convert_to_tensor(seq_len.astype(np.long))

        y, y_len = net(x, x_len)
        assert (y.shape.as_list()[0] == batch)
        if is_channels_first(data_format):
            assert (y.shape.as_list()[1] == classes)
            assert (y.shape.as_list()[2] in [seq_len_max // 2, seq_len_max // 2 + 1])
        else:
            assert (y.shape.as_list()[1] in [seq_len_max // 2, seq_len_max // 2 + 1])
            assert (y.shape.as_list()[2] == classes)

        weight_count = sum([np.prod(K.get_value(w).shape) for w in net.trainable_weights])
        print("m={}, {}".format(model.__name__, weight_count))
        assert (model != jasper5x3 or weight_count == 107681053)
        assert (model != jasper10x4 or weight_count == 261393693)
        assert (model != jasper10x5 or weight_count == 322286877)


if __name__ == "__main__":
    _test()
