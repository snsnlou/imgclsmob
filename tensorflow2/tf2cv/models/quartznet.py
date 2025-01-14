"""
    QuartzNet for ASR, implemented in TensorFlow.
    Original paper: 'QuartzNet: Deep Automatic Speech Recognition with 1D Time-Channel Separable Convolutions,'
    https://arxiv.org/abs/1910.10261.
"""

__all__ = ['quartznet5x5_en_ls', 'quartznet15x5_en', 'quartznet15x5_en_nr', 'quartznet15x5_fr', 'quartznet15x5_de',
           'quartznet15x5_it', 'quartznet15x5_es', 'quartznet15x5_ca', 'quartznet15x5_pl', 'quartznet15x5_ru']

from .jasper import get_jasper
from .common import is_channels_first


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
    root : str, default '~/.tensorflow/models'
        Location for keeping the model parameters.
    """
    vocabulary = [' ', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                  't', 'u', 'v', 'w', 'x', 'y', 'z', "'"]
    return get_jasper(classes=classes, version=("quartznet", "5x5"), use_dw=True, vocabulary=vocabulary,
                      model_name="quartznet5x5_en_ls", **kwargs)


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
    root : str, default '~/.tensorflow/models'
        Location for keeping the model parameters.
    """
    vocabulary = [' ', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                  't', 'u', 'v', 'w', 'x', 'y', 'z', "'"]
    return get_jasper(classes=classes, version=("quartznet", "15x5"), use_dw=True, vocabulary=vocabulary,
                      model_name="quartznet15x5_en", **kwargs)


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
    root : str, default '~/.tensorflow/models'
        Location for keeping the model parameters.
    """
    vocabulary = [' ', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                  't', 'u', 'v', 'w', 'x', 'y', 'z', "'"]
    return get_jasper(classes=classes, version=("quartznet", "15x5"), use_dw=True, vocabulary=vocabulary,
                      model_name="quartznet15x5_en_nr", **kwargs)


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
    root : str, default '~/.tensorflow/models'
        Location for keeping the model parameters.
    """
    vocabulary = [' ', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                  't', 'u', 'v', 'w', 'x', 'y', 'z', "'", 'ç', 'é', 'â', 'ê', 'î', 'ô', 'û', 'à', 'è', 'ù', 'ë', 'ï',
                  'ü', 'ÿ']
    return get_jasper(classes=classes, version=("quartznet", "15x5"), use_dw=True, vocabulary=vocabulary,
                      model_name="quartznet15x5_fr", **kwargs)


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
    root : str, default '~/.tensorflow/models'
        Location for keeping the model parameters.
    """
    vocabulary = [' ', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                  't', 'u', 'v', 'w', 'x', 'y', 'z', 'ä', 'ö', 'ü', 'ß']
    return get_jasper(classes=classes, version=("quartznet", "15x5"), use_dw=True, vocabulary=vocabulary,
                      model_name="quartznet15x5_de", **kwargs)


def quartznet15x5_it(classes=39, **kwargs):
    """
    QuartzNet 15x5 model for Italian language from 'QuartzNet: Deep Automatic Speech Recognition with 1D Time-Channel
    Separable Convolutions,' https://arxiv.org/abs/1910.10261.

    Parameters:
    ----------
    classes : int, default 39
        Number of classification classes (number of graphemes).
    pretrained : bool, default False
        Whether to load the pretrained weights for model.
    root : str, default '~/.tensorflow/models'
        Location for keeping the model parameters.
    """
    vocabulary = [' ', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                  't', 'u', 'v', 'w', 'x', 'y', 'z', "'", 'à', 'é', 'è', 'í', 'ì', 'î', 'ó', 'ò', 'ú', 'ù']
    return get_jasper(classes=classes, version=("quartznet", "15x5"), use_dw=True, vocabulary=vocabulary,
                      model_name="quartznet15x5_it", **kwargs)


def quartznet15x5_es(classes=36, **kwargs):
    """
    QuartzNet 15x5 model for Spanish language from 'QuartzNet: Deep Automatic Speech Recognition with 1D Time-Channel
    Separable Convolutions,' https://arxiv.org/abs/1910.10261.

    Parameters:
    ----------
    classes : int, default 36
        Number of classification classes (number of graphemes).
    pretrained : bool, default False
        Whether to load the pretrained weights for model.
    root : str, default '~/.tensorflow/models'
        Location for keeping the model parameters.
    """
    vocabulary = [' ', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                  't', 'u', 'v', 'w', 'x', 'y', 'z', "'", 'á', 'é', 'í', 'ó', 'ú', 'ñ', 'ü']
    return get_jasper(classes=classes, version=("quartznet", "15x5"), use_dw=True, vocabulary=vocabulary,
                      model_name="quartznet15x5_es", **kwargs)


def quartznet15x5_ca(classes=39, **kwargs):
    """
    QuartzNet 15x5 model for Spanish language from 'QuartzNet: Deep Automatic Speech Recognition with 1D Time-Channel
    Separable Convolutions,' https://arxiv.org/abs/1910.10261.

    Parameters:
    ----------
    classes : int, default 39
        Number of classification classes (number of graphemes).
    pretrained : bool, default False
        Whether to load the pretrained weights for model.
    root : str, default '~/.tensorflow/models'
        Location for keeping the model parameters.
    """
    vocabulary = [' ', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                  't', 'u', 'v', 'w', 'x', 'y', 'z', "'", 'à', 'é', 'è', 'í', 'ï', 'ó', 'ò', 'ú', 'ü', 'ŀ']
    return get_jasper(classes=classes, version=("quartznet", "15x5"), use_dw=True, vocabulary=vocabulary,
                      model_name="quartznet15x5_ca", **kwargs)


def quartznet15x5_pl(classes=34, **kwargs):
    """
    QuartzNet 15x5 model for Spanish language from 'QuartzNet: Deep Automatic Speech Recognition with 1D Time-Channel
    Separable Convolutions,' https://arxiv.org/abs/1910.10261.

    Parameters:
    ----------
    classes : int, default 34
        Number of classification classes (number of graphemes).
    pretrained : bool, default False
        Whether to load the pretrained weights for model.
    root : str, default '~/.tensorflow/models'
        Location for keeping the model parameters.
    """
    vocabulary = [' ', 'a', 'ą', 'b', 'c', 'ć', 'd', 'e', 'ę', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'ł', 'm', 'n', 'ń',
                  'o', 'ó', 'p', 'r', 's', 'ś', 't', 'u', 'w', 'y', 'z', 'ź', 'ż']
    return get_jasper(classes=classes, version=("quartznet", "15x5"), use_dw=True, vocabulary=vocabulary,
                      model_name="quartznet15x5_pl", **kwargs)


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
    root : str, default '~/.tensorflow/models'
        Location for keeping the model parameters.
    """
    vocabulary = [' ', 'а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с',
                  'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я']
    return get_jasper(classes=classes, version=("quartznet", "15x5"), use_dw=True, vocabulary=vocabulary,
                      model_name="quartznet15x5_ru", **kwargs)


def _test():
    import numpy as np
    import tensorflow.keras.backend as K
    import tensorflow as tf

    data_format = "channels_last"
    # data_format = "channels_first"
    pretrained = False
    audio_features = 64

    models = [
        quartznet5x5_en_ls,
        quartznet15x5_en,
        quartznet15x5_en_nr,
        quartznet15x5_fr,
        quartznet15x5_de,
        quartznet15x5_it,
        quartznet15x5_es,
        quartznet15x5_ca,
        quartznet15x5_pl,
        quartznet15x5_ru,
    ]

    for model in models:

        net = model(
            in_channels=audio_features,
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
            assert (y.shape.as_list()[1] == net.classes)
            assert (y.shape.as_list()[2] in [seq_len_max // 2, seq_len_max // 2 + 1])
        else:
            assert (y.shape.as_list()[1] in [seq_len_max // 2, seq_len_max // 2 + 1])
            assert (y.shape.as_list()[2] == net.classes)

        weight_count = sum([np.prod(K.get_value(w).shape) for w in net.trainable_weights])
        print("m={}, {}".format(model.__name__, weight_count))
        assert (model != quartznet5x5_en_ls or weight_count == 6713181)
        assert (model != quartznet15x5_en or weight_count == 18924381)
        assert (model != quartznet15x5_en_nr or weight_count == 18924381)
        assert (model != quartznet15x5_fr or weight_count == 18938731)
        assert (model != quartznet15x5_de or weight_count == 18927456)
        assert (model != quartznet15x5_it or weight_count == 18934631)
        assert (model != quartznet15x5_es or weight_count == 18931556)
        assert (model != quartznet15x5_ca or weight_count == 18934631)
        assert (model != quartznet15x5_pl or weight_count == 18929506)
        assert (model != quartznet15x5_ru or weight_count == 18930531)


if __name__ == "__main__":
    _test()
