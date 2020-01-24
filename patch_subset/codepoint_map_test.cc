#include "patch_subset/codepoint_map.h"

#include "common/status.h"
#include "gtest/gtest.h"
#include "patch_subset/hb_set_unique_ptr.h"

namespace patch_subset {

class CodepointMapTest : public ::testing::Test {
 protected:
  CodepointMapTest() {
    codepoint_map_.AddMapping(7, 0);
    codepoint_map_.AddMapping(3, 1);
    codepoint_map_.AddMapping(4, 2);
  }

  void ExpectEncodes(hb_codepoint_t from, hb_codepoint_t to) {
    hb_codepoint_t cp = from;
    EXPECT_EQ(StatusCode::kOk, codepoint_map_.Encode(&cp));
    EXPECT_EQ(cp, to);
  }

  void ExpectDecodes(hb_codepoint_t from, hb_codepoint_t to) {
    hb_codepoint_t cp = from;
    EXPECT_EQ(StatusCode::kOk, codepoint_map_.Decode(&cp));
    EXPECT_EQ(cp, to);
  }

  CodepointMap codepoint_map_;
};

TEST_F(CodepointMapTest, Clear) {
  codepoint_map_.Clear();

  hb_codepoint_t cp = 7;
  EXPECT_EQ(StatusCode::kInvalidArgument, codepoint_map_.Encode(&cp));
  cp = 3;
  EXPECT_EQ(StatusCode::kInvalidArgument, codepoint_map_.Encode(&cp));
  cp = 4;
  EXPECT_EQ(StatusCode::kInvalidArgument, codepoint_map_.Encode(&cp));
}

TEST_F(CodepointMapTest, EncodeEmptySet) {
  hb_set_unique_ptr codepoints = make_hb_set();
  EXPECT_EQ(StatusCode::kOk, codepoint_map_.Encode(codepoints.get()));
  EXPECT_TRUE(hb_set_is_empty(codepoints.get()));
}

TEST_F(CodepointMapTest, EncodeSet) {
  hb_set_unique_ptr codepoints = make_hb_set(2, 4, 7);
  EXPECT_EQ(StatusCode::kOk, codepoint_map_.Encode(codepoints.get()));

  hb_set_unique_ptr expected = make_hb_set(2, 0, 2);
  EXPECT_TRUE(hb_set_is_equal(codepoints.get(), expected.get()));
}

TEST_F(CodepointMapTest, EncodeSingle) {
  ExpectEncodes(7, 0);
  ExpectEncodes(3, 1);
  ExpectEncodes(4, 2);
}

TEST_F(CodepointMapTest, EncodeMissing) {
  hb_set_unique_ptr codepoints = make_hb_set(3, 2, 4, 7);
  EXPECT_EQ(StatusCode::kInvalidArgument,
            codepoint_map_.Encode(codepoints.get()));

  hb_codepoint_t missing_cp = 2;
  EXPECT_EQ(StatusCode::kInvalidArgument, codepoint_map_.Encode(&missing_cp));
}

TEST_F(CodepointMapTest, DecodeSet) {
  hb_set_unique_ptr codepoints = make_hb_set();
  EXPECT_EQ(StatusCode::kOk, codepoint_map_.Decode(codepoints.get()));
  EXPECT_TRUE(hb_set_is_empty(codepoints.get()));
}

TEST_F(CodepointMapTest, DecodeSingle) {
  ExpectDecodes(0, 7);
  ExpectDecodes(1, 3);
  ExpectDecodes(2, 4);
}

TEST_F(CodepointMapTest, DecodeEmptySet) {
  hb_set_unique_ptr codepoints = make_hb_set(2, 0, 2);
  EXPECT_EQ(StatusCode::kOk, codepoint_map_.Decode(codepoints.get()));

  hb_set_unique_ptr expected = make_hb_set(2, 4, 7);
  EXPECT_TRUE(hb_set_is_equal(codepoints.get(), expected.get()));
}

TEST_F(CodepointMapTest, DecodeMissing) {
  hb_set_unique_ptr codepoints = make_hb_set(3, 0, 2, 3);
  EXPECT_EQ(StatusCode::kInvalidArgument,
            codepoint_map_.Decode(codepoints.get()));

  hb_codepoint_t missing_cp = 3;
  EXPECT_EQ(StatusCode::kInvalidArgument, codepoint_map_.Decode(&missing_cp));
}

TEST_F(CodepointMapTest, ToProto) {
  CodepointRemappingProto proto;

  EXPECT_EQ(StatusCode::kOk, codepoint_map_.ToProto(&proto));

  EXPECT_EQ(proto.fingerprint(), 0u);
  EXPECT_TRUE(proto.grouping_strategy().empty());

  EXPECT_EQ(proto.codepoint_ordering().deltas_size(), 3);
  EXPECT_EQ(proto.codepoint_ordering().deltas(0), 7);
  EXPECT_EQ(proto.codepoint_ordering().deltas(1), -4);
  EXPECT_EQ(proto.codepoint_ordering().deltas(2), 1);
}

}  // namespace patch_subset
