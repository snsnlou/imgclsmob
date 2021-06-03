"""
    QuartzNet for ASR, implemented in Gluon.
    Original paper: 'QuartzNet: Deep Automatic Speech Recognition with 1D Time-Channel Separable Convolutions,'
    https://arxiv.org/abs/1910.10261.
"""

__all__ = ['quartznet5x5_en_ls', 'quartznet15x5_en', 'quartznet15x5_en_nr', 'quartznet15x5_fr', 'quartznet15x5_de',
           'quartznet15x5_ru']

from .jasper import get_jasper


def quartznet5x5_en_ls(classes=29, **kwargs):
    """
    QuartzNet 15x5 model for English language (trained on LibriSpeech dataset) from 'QuartzNet: Deep Automatic Speech
    Recognition with 1D Time-Channel Separable Convolutions,' https://arxiv.org/abs/1910.10261.

    Parameters:
    ----------
    classes : int, default 29
        Number of classification classes (number of graphemes).
    pretrained : bool, default False
        Whether to load the pretrained weights for model.
    ctx : Context, default CPU
        The context in which to load the pretrained weights.
    root : str, default '~/.mxnet/models'
        Location for keeping the model parameters.
    """
    return get_jasper(classes=classes, version=("quartznet", "5x5"), use_dw=True, model_name="quartznet5x5_en_ls",
                      **kwargs)


def quartznet15x5_en(classes=29, **kwargs):
    """
    QuartzNet 15x5 model for English language from 'QuartzNet: Deep Automatic Speech Recognition with 1D Time-Channel
    Separable Convolutions,' https://arxiv.org/abs/1910.10261.

    Parameters:
    ----------
    classes : int, default 29
        Number of classification classes (number of graphemes).
    pretrained : bool, default False
        Whether to load the pretrained weights for model.
    ctx : Context, default CPU
        The context in which to load the pretrained weights.
    root : str, default '~/.mxnet/models'
        Location for keeping the model parameters.
    """
    return get_jasper(classes=classes, version=("quartznet", "15x5"), use_dw=True, model_name="quartznet15x5_en",
                      **kwargs)


def quartznet15x5_en_nr(classes=29, **kwargs):
    """
    QuartzNet 15x5 model for English language (with presence of noise) from 'QuartzNet: Deep Automatic Speech
    Recognition with 1D Time-Channel Separable Convolutions,' https://arxiv.org/abs/1910.10261.

    Parameters:
    ----------
    classes : int, default 29
        Number of classification classes (number of graphemes).
    pretrained : bool, default False
        Whether to load the pretrained weights for model.
    ctx : Context, default CPU
        The context in which to load the pretrained weights.
    root : str, default '~/.mxnet/models'
        Location for keeping the model parameters.
    """
    return get_jasper(classes=classes, version=("quartznet", "15x5"), use_dw=True, model_name="quartznet15x5_en_nr",
                      **kwargs)


def quartznet15x5_fr(classes=43, **kwargs):
    """
    QuartzNet 15x5 model for French language from 'QuartzNet: Deep Automatic Speech Recognition with 1D Time-Channel
    Separable Convolutions,' https://arxiv.org/abs/1910.10261.

    Parameters:
    ----------
    classes : int, default 29
        Number of classification classes (number of graphemes).
    pretrained : bool, default False
        Whether to load the pretrained weights for model.
    ctx : Context, default CPU
        The context in which to load the pretrained weights.
    root : str, default '~/.mxnet/models'
        Location for keeping the model parameters.
    """
    return get_jasper(classes=classes, version=("quartznet", "15x5"), use_dw=True, model_name="quartznet15x5_fr",
                      **kwargs)


def quartznet15x5_de(classes=32, **kwargs):
    """
    QuartzNet 15x5 model for German language from 'QuartzNet: Deep Automatic Speech Recognition with 1D Time-Channel
    Separable Convolutions,' https://arxiv.org/abs/1910.10261.

    Parameters:
    ----------
    classes : int, default 29
        Number of classification classes (number of graphemes).
    pretrained : bool, default False
        Whether to load the pretrained weights for model.
    ctx : Context, default CPU
        The context in which to load the pretrained weights.
    root : str, default '~/.mxnet/models'
        Location for keeping the model parameters.
    """
    return get_jasper(classes=classes, version=("quartznet", "15x5"), use_dw=True,
                      model_name="quartznet15x5_de", **kwargs)


def quartznet15x5_ru(classes=35, **kwargs):
    """
    QuartzNet 15x5 model for Russian language from 'QuartzNet: Deep Automatic Speech Recognition with 1D Time-Channel
    Separable Convolutions,' https://arxiv.org/abs/1910.10261.

    Parameters:
    ----------
    classes : int, default 35
        Number of classification classes (number of graphemes).
    pretrained : bool, default False
        Whether to load the pretrained weights for model.
    ctx : Context, default CPU
        The context in which to load the pretrained weights.
    root : str, default '~/.mxnet/models'
        Location for keeping the model parameters.
    """
    return get_jasper(classes=classes, version=("quartznet", "15x5"), use_dw=True, model_name="quartznet15x5_ru",
                      **kwargs)


def _calc_width(net):
    import numpy as np
    net_params = net.collect_params()
    weight_count = 0
    for param in net_params.values():
        if (param.shape is None) or (not param._differentiable):
            continue
        weight_count += np.prod(param.shape)
    return weight_count


def _test():
    import numpy as np
    import mxnet as mx

    pretrained = False
    audio_features = 64

    models = [
        quartznet5x5_en_ls,
        quartznet15x5_en,
        quartznet15x5_en_nr,
        quartznet15x5_fr,
        quartznet15x5_de,
        quartznet15x5_ru,
    ]

    for model in models:

        net = model(
            in_channels=audio_features,
            pretrained=pretrained)

        ctx = mx.cpu()
        if not pretrained:
            net.initialize(ctx=ctx)

        # net.hybridize()
        weight_count = _calc_width(net)
        print("m={}, {}".format(model.__name__, weight_count))
        assert (model != quartznet5x5_en_ls or weight_count == 6713181)
        assert (model != quartznet15x5_en or weight_count == 18924381)
        assert (model != quartznet15x5_en_nr or weight_count == 18924381)
        assert (model != quartznet15x5_fr or weight_count == 18938731)
        assert (model != quartznet15x5_de or weight_count == 18927456)
        assert (model != quartznet15x5_ru or weight_count == 18930531)

        batch = 3
        seq_len = np.random.randint(60, 150, batch)
        seq_len_max = seq_len.max() + 2
        x = mx.nd.random.normal(shape=(batch, audio_features, seq_len_max), ctx=ctx)
        x_len = mx.nd.array(seq_len, ctx=ctx, dtype=np.long)

        y, y_len = net(x, x_len)
        assert (y.shape[:2] == (batch, net.classes))
        assert (y.shape[2] in [seq_len_max // 2, seq_len_max // 2 + 1])


if __name__ == "__main__":
    _test()
