workspace(name = "PFE_analysis")
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

# Google Test
http_archive(
    name = "gtest",
    url = "https://github.com/google/googletest/archive/master.zip",
    strip_prefix = "googletest-master",
)

# Brotli Encoder/Decoder
http_archive(
    name = "brotli",
    url = "https://github.com/google/brotli/archive/shared-brotli.zip",
    strip_prefix = "brotli-shared-brotli",
)

# harfbuzz
http_archive(
    name = "harfbuzz",
    build_file = "//third_party:harfbuzz.BUILD",
    strip_prefix = "harfbuzz-master",
    urls = ["https://github.com/harfbuzz/harfbuzz/archive/master.zip"],
)

# farmhash
http_archive(
    name = "farmhash",
    build_file = "//third_party:farmhash.BUILD",
    strip_prefix = "farmhash-master",
    urls = ["https://github.com/google/farmhash/archive/master.zip"],
)

# abseil-cpp
http_archive(
     name = "com_google_absl",
     urls = ["https://github.com/abseil/abseil-cpp/archive/master.zip"],
     strip_prefix = "abseil-cpp-master",
)

# abseil-py
http_archive(
     name = "io_abseil_py",
     urls = ["https://github.com/abseil/abseil-py/archive/master.zip"],
     strip_prefix = "abseil-py-master",
)

# six archive - needed by abseil-py
http_archive(
    name = "six_archive",
    urls = [
        "http://mirror.bazel.build/pypi.python.org/packages/source/s/six/six-1.10.0.tar.gz",
        "https://pypi.python.org/packages/source/s/six/six-1.10.0.tar.gz",
    ],
    sha256 = "105f8d68616f8248e24bf0e9372ef04d3cc10104f1980f54d57b2ce73a5ad56a",
    strip_prefix = "six-1.10.0",
    build_file = "@//third_party:six.BUILD",
)

# rules_cc defines rules for generating C++ code from Protocol Buffers.
http_archive(
    name = "rules_cc",
    strip_prefix = "rules_cc-master",
    urls = ["https://github.com/bazelbuild/rules_cc/archive/master.zip"],
)

# rules_proto defines abstract rules for building Protocol Buffers.
http_archive(
    name = "rules_proto",
    strip_prefix = "rules_proto-master",
    urls = [
        "https://github.com/bazelbuild/rules_proto/archive/master.zip",
    ],
)

load("@rules_cc//cc:repositories.bzl", "rules_cc_dependencies")
rules_cc_dependencies()

load("@rules_proto//proto:repositories.bzl", "rules_proto_dependencies", "rules_proto_toolchains")
rules_proto_dependencies()
rules_proto_toolchains()
