from enum import Enum

from mace.proto import mace_pb2


class DataFormat(Enum):
    NHWC = 0
    NCHW = 1


class FilterFormat(Enum):
    HWIO = 0
    OIHW = 1
    HWOI = 2


class PaddingMode(Enum):
    VALID = 0
    SAME = 1
    FULL = 2


class PoolingType(Enum):
    AVG = 1
    MAX = 2


class ActivationType(Enum):
    NOOP = 0
    RELU = 1
    RELUX = 2
    PRELU = 3
    TANH = 4
    SIGMOID = 5


class EltwiseType(Enum):
    SUM = 0
    SUB = 1
    PROD = 2
    DIV = 3
    MIN = 4
    MAX = 5
    NEG = 6
    ABS = 7
    SQR_DIFF = 8
    POW = 9


MaceSupportedOps = [
    'Activation',
    'AddN',
    'BatchNorm',
    'BatchToSpaceND',
    'BiasAdd',
    'ChannelShuffle',
    'Concat',
    'Conv2D',
    'Deconv2D',
    'DepthToSpace',
    'DepthwiseConv2d',
    'Dequantize',
    'Eltwise',
    'FoldedBatchNorm',
    'FullyConnected',
    'LocalResponseNorm',
    'MatMul',
    'Pad',
    'Pooling',
    'Proposal',
    'PSROIAlign',
    'Quantize',
    'Requantize',
    'Reshape',
    'ResizeBilinear',
    'Slice',
    'Softmax',
    'SpaceToBatchND',
    'SpaceToDepth',
    'Transpose',
    'WinogradInverseTransform',
    'WinogradTransform',
]

MaceOp = Enum('MaceOp', [(op, op) for op in MaceSupportedOps], type=str)


class MaceKeyword(object):
    # node related str
    mace_input_node_name = 'mace_input_node'
    mace_output_node_name = 'mace_output_node'
    mace_buffer_type = 'buffer_type'
    mace_mode = 'mode'
    mace_buffer_to_image = 'BufferToImage'
    mace_image_to_buffer = 'ImageToBuffer'
    # arg related str
    mace_padding_str = 'padding'
    mace_padding_values_str = 'padding_values'
    mace_strides_str = 'strides'
    mace_dilations_str = 'dilations'
    mace_pooling_type_str = 'pooling_type'
    mace_global_pooling_str = 'global_pooling'
    mace_kernel_str = 'kernels'
    mace_data_format_str = 'data_format'
    mace_filter_format_str = 'filter_format'
    mace_element_type_str = 'type'
    mace_activation_type_str = 'activation'
    mace_activation_max_limit_str = 'max_limit'
    mace_resize_size_str = 'size'
    mace_batch_to_space_crops_str = 'crops'
    mace_paddings_str = 'paddings'
    mace_align_corners_str = 'align_corners'
    mace_space_batch_block_shape_str = 'block_shape'
    mace_space_depth_block_size_str = 'block_size'
    mace_constant_value_str = 'constant_value'
    mace_dims_str = 'dims'
    mace_axis_str = 'axis'
    mace_shape_str = 'shape'
    mace_winograd_filter_transformed = 'is_filter_transformed'


class ConverterInterface(object):
    """Base class for converting external models to mace models."""

    def run(self):
        raise NotImplementedError('run')


class NodeInfo(object):
    """A class for describing node information"""

    def __init__(self):
        self._name = None
        self._shape = []

    @property
    def name(self):
        return self._name

    @property
    def shape(self):
        return self._shape

    @name.setter
    def name(self, name):
        self._name = name

    @shape.setter
    def shape(self, shape):
        self._shape = shape

    def __str__(self):
        return '%s %s' % (self._name, str(self._shape))


class ConverterOption(object):
    """A class for specifying options passed to converter tool"""

    def __init__(self):
        self._input_nodes = {}
        self._output_nodes = {}
        self._data_type = mace_pb2.DT_FLOAT
        self._device = mace_pb2.CPU
        self._winograd_enabled = False

    @property
    def input_nodes(self):
        return self._input_nodes

    @property
    def output_nodes(self):
        return self._output_nodes

    @property
    def data_type(self):
        return self._data_type

    @property
    def device(self):
        return self._device

    @property
    def winograd_enabled(self):
        return self._winograd_enabled

    @input_nodes.setter
    def input_nodes(self, input_nodes):
        for node in input_nodes:
            self._input_nodes[node.name] = node

    def add_input_node(self, input_node):
        self._input_nodes[input_node.name] = input_node

    @output_nodes.setter
    def output_nodes(self, output_nodes):
        for node in output_nodes:
            self.output_nodes[node.name] = node

    def add_output_node(self, output_node):
        self._output_nodes[output_node.name] = output_node

    @data_type.setter
    def data_type(self, data_type):
        self._data_type = data_type

    @device.setter
    def device(self, device):
        self._device = device

    @winograd_enabled.setter
    def winograd_enabled(self, winograd_enabled):
        self._winograd_enabled = winograd_enabled


class ConverterUtil(object):
    @staticmethod
    def get_arg(op, arg_name):
        for arg in op.arg:
            if arg.name == arg_name:
                return arg
        return None

    @staticmethod
    def add_data_format_arg(op, data_format):
        data_format_arg = op.arg.add()
        data_format_arg.name = MaceKeyword.mace_data_format_str
        data_format_arg.i = data_format.value

    @staticmethod
    def data_format(op):
        arg = ConverterUtil.get_arg(op, MaceKeyword.mace_data_format_str)
        if arg is None:
            return None
        elif arg.i == DataFormat.NHWC.value:
            return DataFormat.NHWC
        elif arg.i == DataFormat.NCHW.value:
            return DataFormat.NCHW
        else:
            return None

    @staticmethod
    def set_filter_format(net, filter_format):
        arg = net.arg.add()
        arg.name = MaceKeyword.mace_filter_format_str
        arg.i = filter_format.value

    @staticmethod
    def filter_format(net):
        arg = ConverterUtil.get_arg(net, MaceKeyword.mace_filter_format_str)
        if arg is None:
            return None
        elif arg.i == FilterFormat.HWIO.value:
            return FilterFormat.HWIO
        elif arg.i == FilterFormat.HWOI.value:
            return FilterFormat.HWOI
        elif arg.i == FilterFormat.OIHW.value:
            return FilterFormat.OIHW
        else:
            return None