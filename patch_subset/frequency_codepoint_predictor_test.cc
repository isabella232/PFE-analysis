#include "patch_subset/frequency_codepoint_predictor.h"

#include <memory>

#include "analysis/pfe_methods/unicode_range_data/slicing_strategy.pb.h"
#include "common/status.h"
#include "gtest/gtest.h"
#include "patch_subset/hb_set_unique_ptr.h"

using analysis::pfe_methods::unicode_range_data::Codepoint;
using analysis::pfe_methods::unicode_range_data::SlicingStrategy;
using analysis::pfe_methods::unicode_range_data::Subset;

namespace patch_subset {

class FrequencyCodepointPredictorTest : public ::testing::Test {
 protected:
  FrequencyCodepointPredictorTest()
      : predictor_(FrequencyCodepointPredictor::Create(
            "patch_subset/testdata/strategies/")) {}

  std::unique_ptr<CodepointPredictor> predictor_;
};

TEST_F(FrequencyCodepointPredictorTest, Predict) {
  hb_set_unique_ptr font_codepoints = make_hb_set_from_ranges(1, 65, 75);
  hb_set_unique_ptr requested_codepoints = make_hb_set_from_ranges(1, 68, 69);
  hb_set_unique_ptr result = make_hb_set();

  predictor_->Predict(font_codepoints.get(), requested_codepoints.get(), 2,
                      result.get());

  hb_set_unique_ptr expected = make_hb_set(2, 66, 67);
  EXPECT_TRUE(hb_set_is_equal(result.get(), expected.get()));
}

TEST_F(FrequencyCodepointPredictorTest, PredictDuplicateCounts) {
  hb_set_unique_ptr font_codepoints = make_hb_set_from_ranges(1, 95, 99);
  hb_set_unique_ptr requested_codepoints = make_hb_set(1, 95);
  hb_set_unique_ptr result = make_hb_set();

  predictor_->Predict(font_codepoints.get(), requested_codepoints.get(), 3,
                      result.get());

  hb_set_unique_ptr expected = make_hb_set(3, 96, 97, 98);
  EXPECT_TRUE(hb_set_is_equal(result.get(), expected.get()));
}

TEST_F(FrequencyCodepointPredictorTest, PredictMultipleSubsets) {
  hb_set_unique_ptr font_codepoints = make_hb_set_from_ranges(1, 65, 75);
  hb_set_unique_ptr requested_codepoints =
      make_hb_set_from_ranges(2, 68, 69, 75, 76);
  hb_set_unique_ptr result = make_hb_set();

  predictor_->Predict(font_codepoints.get(), requested_codepoints.get(), 3,
                      result.get());

  hb_set_unique_ptr expected = make_hb_set(3, 67, 78, 79);
  EXPECT_TRUE(hb_set_is_equal(result.get(), expected.get()));
}

TEST_F(FrequencyCodepointPredictorTest, PredictUseHighestCoverageStrategy) {
  hb_set_unique_ptr font_codepoints =
      make_hb_set_from_ranges(2, 65, 65, 85, 89);
  hb_set_unique_ptr requested_codepoints = make_hb_set(2, 85, 86);
  hb_set_unique_ptr result = make_hb_set();

  predictor_->Predict(font_codepoints.get(), requested_codepoints.get(), 2,
                      result.get());

  hb_set_unique_ptr expected = make_hb_set(2, 88, 89);
  EXPECT_TRUE(hb_set_is_equal(result.get(), expected.get()));
}

}  // namespace patch_subset
