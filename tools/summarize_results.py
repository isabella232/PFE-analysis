"""Provides summaries of the results of an analysis

Takes an AnalysisResultProto in either text or binary form and can
Summarize the data in a few different ways. See USAGE string below.
"""

import sys

from absl import app
from absl import flags
from analysis import result_pb2
from google.protobuf import text_format

USAGE = """Usage:

summarize_results [--input_file=<path to input>] <mode>

Available modes:
  cost_summary - print out the total cost for each method and network model.
  request_size_distribution <method> - print out the request size distribution for a particular method.
  response_size_distribution <method> - print out the request size distribution for a particular method.
  latency_distriubtion <method> <network> - print out the latency distribution for a particular method and network model.
  cost_distriubtion <method> <network> - print out the cost distribution for a particular method and network model.
"""

FLAGS = flags.FLAGS
flags.DEFINE_string(
    "input_file", "-",
    "Path to a file containing an analysis result proto or '-' to read from stdin."
)

flags.DEFINE_bool("binary", False,
                  "If true, will parse the input file as a binary proto.")


class NetworkResultNotFound(Exception):
  """Could not find the specified network result."""


class MethodResultNotFound(Exception):
  """Could not find the specified method result."""


MODE_FUNCTIONS = {
    "cost_summary":
        lambda argv, result_proto: print_cost_summary(result_proto),
    "latency_distribution":
        (lambda argv, result_proto: print_network_distribution(
            argv, result_proto, "request_latency_distribution")),
    "cost_distribution": (lambda argv, result_proto: print_network_distribution(
        argv, result_proto, "cost_distribution")),
    "request_size_distribution":
        (lambda argv, result_proto: print_method_distribution(
            argv, result_proto, "request_size_distribution")),
    "response_size_distribution":
        (lambda argv, result_proto: print_method_distribution(
            argv, result_proto, "response_size_distribution")),
}


def main(argv):  # pylint: disable=missing-function-docstring
  result_proto = result_pb2.AnalysisResultProto()
  if not FLAGS.binary:
    input_file_contents = read_input(FLAGS.input_file)
    text_format.Merge(input_file_contents, result_proto)
  else:
    input_file_contents = read_binary_input(FLAGS.input_file)
    result_proto.ParseFromString(input_file_contents)

  if len(argv) < 2:
    return print_usage()

  mode = argv[1]
  argv = argv[2:]
  if mode not in MODE_FUNCTIONS:
    return print_usage()

  return MODE_FUNCTIONS[mode](argv, result_proto)


def print_method_distribution(argv, result_proto, property_name):
  """Find and print a distribution found on a MethodResultProto."""
  if len(argv) < 1:
    print_usage()
    return

  method = argv[0]
  method_proto = find_method_result(method, result_proto)
  dist_proto = getattr(method_proto, property_name)
  print_distribution(dist_proto)


def print_network_distribution(argv, result_proto, property_name):
  """Find and print a distribution found on a NetworkResultProto."""
  if len(argv) < 2:
    print_usage()
    return

  method = argv[0]
  network = argv[1]

  network_proto = find_network_result(method, network, result_proto)
  dist_proto = getattr(network_proto, property_name)
  print_distribution(dist_proto)


def find_method_result(method, result_proto):
  """Locates the method result proto for method inside of result_proto."""
  matches = [
      method_proto for method_proto in result_proto.results
      if method_proto.method_name == method
  ]

  if len(matches) != 1:
    raise MethodResultNotFound("Cannot find method result %s." % method)

  return matches[0]


def find_network_result(method, network, result_proto):
  """Locates the network result proto for method and network inside of result_proto."""
  method_proto = find_method_result(method, result_proto)
  matches = [
      network_proto for network_proto in method_proto.results_by_network
      if network_proto.network_model_name == network
  ]

  if len(matches) != 1:
    raise NetworkResultNotFound("Cannot find network result for %s and %s." %
                                (method, network))

  return matches[0]


def print_distribution(distribution_proto):
  for bucket in distribution_proto.buckets:
    print("{}, {}".format(bucket.end, bucket.count))


def print_usage():  # pylint: disable=missing-function-docstring
  print(USAGE)
  return -1


def print_cost_summary(result_proto):
  """Converts the result proto into CSV with 3 columns:

  method name, network model name, total cost
  """
  for method_proto in result_proto.results:
    for net_proto in method_proto.results_by_network:
      print("{}, {}, {:.1f}".format(
          method_proto.method_name,
          net_proto.network_model_name,
          net_proto.total_cost,
      ))


def read_input(input_file_path):
  """Read the contents of input_file_path and return them."""
  if input_file_path == "-":
    return sys.stdin.read()

  with open(input_file_path, 'r') as input_data_file:
    return input_data_file.read()


def read_binary_input(input_file_path):
  """Read the contents of input_file_path and return them."""
  if input_file_path == "-":
    return sys.stdin.buffer.read()

  with open(input_file_path, 'rb') as input_data_file:
    return input_data_file.read()


if __name__ == '__main__':
  app.run(main)