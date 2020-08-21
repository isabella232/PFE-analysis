"""Unit tests for the analyzer module."""

import unittest
from analysis import analyzer
from analysis import result_pb2
from analysis import simulation


def mock_cost(total_time_ms):
  return total_time_ms / 10


def s(values):  # pylint: disable=invalid-name
  return simulation.SequenceTotals(values)


def g(time, request, response):  # pylint: disable=invalid-name
  return simulation.GraphTotal(time, request, response, 0)


class AnalyzerTest(unittest.TestCase):

  def test_to_network_category_protos(self):
    cost_function = lambda cost: cost * 2
    network_totals = {
        "desktop_slowest": [
            s([
                g(100, 200, 300),
                g(200, 300, 400),
                g(300, 400, 500),
            ]),
            s([
                g(200, 300, 400),
                g(300, 400, 500),
            ]),
        ],
        "desktop_median": [
            s([
                g(10, 20, 30),
                g(20, 30, 40),
            ]),
            s([
                g(30, 40, 50),
            ]),
        ],
        "mobile_wifi_slowest": [
            s([g(1, 2, 3)]),
            s([g(4, 5, 6)]),
        ]
    }

    result = analyzer.to_network_category_protos(network_totals, cost_function)

    self.assertEqual(len(result), 2)
    self.assertEqual(result[0].network_category, "desktop")
    self.assertEqual(len(result[0].cost_per_sequence), 2)
    self.assertEqual(len(result[0].bytes_per_sequence), 2)

    self.assertEqual(result[1].network_category, "wifi")
    self.assertEqual(len(result[1].cost_per_sequence), 2)
    self.assertEqual(len(result[1].bytes_per_sequence), 2)

    # s0:
    #  cost =   0.05 * 2 * (100 + 200 + 300)
    #         + 0.50 * 2 * (10 + 20)
    #  bytes =  0.05 * (200 + 300 + 300 + 400 + 400 + 500)
    #         + 0.50 * (20 + 30 + 30 + 40)
    self.assertEqual(result[0].cost_per_sequence[0], 90)
    self.assertEqual(result[0].bytes_per_sequence[0], 165)

    # s1:
    #  cost =   0.05 * 2 * (200 + 300)
    #         + 0.50 * 2 * (30)
    #  bytes =  0.05 * (300 + 400 + 400 + 500)
    #         + 0.50 * (40 + 50)
    self.assertEqual(result[0].cost_per_sequence[1], 80)
    self.assertEqual(result[0].bytes_per_sequence[1], 125)

  def test_result_to_protos(self):
    method_proto = result_pb2.MethodResultProto()
    method_proto.method_name = "Fake_PFE"

    network_proto = result_pb2.NetworkResultProto()
    network_proto.network_model_name = "fast"
    network_proto.total_cost = 40
    network_proto.total_wait_time_ms = 400
    network_proto.wait_per_page_view_ms.buckets.add(end=200)
    network_proto.wait_per_page_view_ms.buckets.add(end=205, count=2)
    network_proto.cost_per_page_view.buckets.add(end=20)
    network_proto.cost_per_page_view.buckets.add(end=25, count=2)
    network_proto.request_bytes_per_page_view.buckets.add(end=1000)
    network_proto.request_bytes_per_page_view.buckets.add(end=1005, count=2)
    network_proto.response_bytes_per_page_view.buckets.add(end=2000)
    network_proto.response_bytes_per_page_view.buckets.add(end=2005, count=2)
    network_proto.total_request_bytes = 2000
    network_proto.total_response_bytes = 4000
    network_proto.total_request_count = 12
    method_proto.results_by_network.append(network_proto)

    network_proto = result_pb2.NetworkResultProto()
    network_proto.network_model_name = "slow"
    network_proto.total_cost = 420
    network_proto.total_wait_time_ms = 4200
    network_proto.wait_per_page_view_ms.buckets.add(end=2100)
    network_proto.wait_per_page_view_ms.buckets.add(end=2105, count=2)
    network_proto.cost_per_page_view.buckets.add(end=210)
    network_proto.cost_per_page_view.buckets.add(end=215, count=2)
    network_proto.request_bytes_per_page_view.buckets.add(end=1000)
    network_proto.request_bytes_per_page_view.buckets.add(end=1005, count=2)
    network_proto.response_bytes_per_page_view.buckets.add(end=2000)
    network_proto.response_bytes_per_page_view.buckets.add(end=2005, count=2)
    network_proto.total_request_bytes = 2000
    network_proto.total_response_bytes = 4000
    network_proto.total_request_count = 12
    method_proto.results_by_network.append(network_proto)

    self.assertEqual(
        analyzer.to_protos(
            {
                "Fake_PFE": {
                    "slow": [
                        simulation.SequenceTotals([
                            simulation.GraphTotal(2100, 1000, 2000, 5),
                            simulation.GraphTotal(2100, 1000, 2000, 7)
                        ]),
                    ],
                    "fast": [
                        simulation.SequenceTotals([
                            simulation.GraphTotal(200, 1000, 2000, 5),
                        ]),
                        simulation.SequenceTotals(
                            [simulation.GraphTotal(200, 1000, 2000, 7)]),
                    ]
                }
            }, mock_cost), [method_proto])

  def test_segment_sequences(self):
    self.assertEqual([], analyzer.segment_sequences([], 3))
    self.assertEqual([[1, 2, 3, 4, 5, 6, 7, 8, 9]],
                     analyzer.segment_sequences([1, 2, 3, 4, 5, 6, 7, 8, 9], 1))
    self.assertEqual([[1, 2, 3, 4], [5, 6, 7, 8], [9]],
                     analyzer.segment_sequences([1, 2, 3, 4, 5, 6, 7, 8, 9], 2))
    self.assertEqual([[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                     analyzer.segment_sequences([1, 2, 3, 4, 5, 6, 7, 8, 9], 3))
    self.assertEqual([[1], [2], [3], [4], [5], [6], [7], [8], [9]],
                     analyzer.segment_sequences([1, 2, 3, 4, 5, 6, 7, 8, 9], 9))
    self.assertEqual([[1], [2], [3], [4], [5], [6], [7], [8], [9]],
                     analyzer.segment_sequences([1, 2, 3, 4, 5, 6, 7, 8, 9],
                                                10))

  def test_merge_results(self):
    self.assertEqual(analyzer.merge_results([]), dict())
    self.assertEqual(analyzer.merge_results([{
        "abc": {
            "def": [1]
        }
    }]), {"abc": {
        "def": [1]
    }})

    self.assertEqual(analyzer.merge_results([
        {
            "abc": {
                "def": [1]
            }
        },
        {},
    ]), {"abc": {
        "def": [1]
    }})

    self.assertEqual(
        analyzer.merge_results([
            {
                "abc": {
                    "jkl": [1]
                }
            },
            {
                "def": {
                    "ghi": [2]
                }
            },
        ]), {
            "abc": {
                "jkl": [1]
            },
            "def": {
                "ghi": [2]
            }
        })

    self.assertEqual(
        analyzer.merge_results([
            {
                "abc": {
                    "jkl": [1]
                }
            },
            {
                "abc": {
                    "jkl": [2]
                }
            },
        ]), {
            "abc": {
                "jkl": [1, 2]
            },
        })

    self.assertEqual(
        analyzer.merge_results([
            {
                "abc": {
                    "jkl": [1]
                }
            },
            {
                "abc": {
                    "jkl": [2]
                }
            },
            {
                "mno": {
                    "jkl": [3]
                }
            },
        ]), {
            "abc": {
                "jkl": [1, 2]
            },
            "mno": {
                "jkl": [3]
            },
        })

    self.assertEqual(
        analyzer.merge_results([
            {
                "abc": {
                    "jkl": [1]
                }
            },
            {
                "abc": {
                    "mno": [2]
                }
            },
        ]), {
            "abc": {
                "jkl": [1],
                "mno": [2]
            },
        })


if __name__ == '__main__':
  unittest.main()
