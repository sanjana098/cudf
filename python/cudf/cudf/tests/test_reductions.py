# Copyright (c) 2020-2024, NVIDIA CORPORATION.


from decimal import Decimal
from itertools import product

import numpy as np
import pandas as pd
import pytest

import cudf
from cudf import Series
from cudf.core.dtypes import Decimal32Dtype, Decimal64Dtype, Decimal128Dtype
from cudf.testing import _utils as utils
from cudf.testing._utils import (
    NUMERIC_TYPES,
    assert_eq,
    expect_warning_if,
    gen_rand,
)

params_dtype = NUMERIC_TYPES

params_sizes = [1, 2, 3, 127, 128, 129, 200, 10000]

params = list(product(params_dtype, params_sizes))


@pytest.mark.parametrize("dtype,nelem", params)
def test_sum(dtype, nelem):
    dtype = cudf.dtype(dtype).type
    data = gen_rand(dtype, nelem)
    sr = Series(data)

    got = sr.sum()
    expect = data.sum()
    significant = 4 if dtype == np.float32 else 6
    np.testing.assert_approx_equal(expect, got, significant=significant)


def test_sum_string():
    s = Series(["Hello", "there", "World"])

    got = s.sum()
    expected = "HellothereWorld"

    assert got == expected

    s = Series(["Hello", None, "World"])

    got = s.sum()
    expected = "HelloWorld"

    assert got == expected


@pytest.mark.parametrize(
    "dtype",
    [
        Decimal64Dtype(6, 3),
        Decimal64Dtype(10, 6),
        Decimal64Dtype(16, 7),
        Decimal32Dtype(6, 3),
        Decimal128Dtype(20, 7),
    ],
)
@pytest.mark.parametrize("nelem", params_sizes)
def test_sum_decimal(dtype, nelem):
    np.random.seed(0)
    data = [str(x) for x in gen_rand("int64", nelem) / 100]

    expected = pd.Series([Decimal(x) for x in data]).sum()
    got = cudf.Series(data).astype(dtype).sum()

    assert_eq(expected, got)


@pytest.mark.parametrize("dtype,nelem", params)
def test_product(dtype, nelem):
    np.random.seed(0)
    dtype = cudf.dtype(dtype).type
    if cudf.dtype(dtype).kind in {"u", "i"}:
        data = np.ones(nelem, dtype=dtype)
        # Set at most 30 items to [0..2) to keep the value within 2^32
        for _ in range(30):
            data[np.random.randint(low=0, high=nelem, size=1)] = (
                np.random.uniform() * 2
            )
    else:
        data = gen_rand(dtype, nelem)

    sr = Series(data)

    got = sr.product()
    expect = pd.Series(data).product()
    significant = 4 if dtype == np.float32 else 6
    np.testing.assert_approx_equal(expect, got, significant=significant)


@pytest.mark.parametrize(
    "dtype",
    [
        Decimal64Dtype(6, 2),
        Decimal64Dtype(8, 4),
        Decimal64Dtype(10, 5),
        Decimal32Dtype(6, 2),
        Decimal128Dtype(20, 5),
    ],
)
def test_product_decimal(dtype):
    np.random.seed(0)
    data = [str(x) for x in gen_rand("int8", 3) / 10]

    expected = pd.Series([Decimal(x) for x in data]).product()
    got = cudf.Series(data).astype(dtype).product()

    assert_eq(expected, got)


accuracy_for_dtype = {np.float64: 6, np.float32: 5}


@pytest.mark.parametrize("dtype,nelem", params)
def test_sum_of_squares(dtype, nelem):
    dtype = cudf.dtype(dtype).type
    data = gen_rand(dtype, nelem)
    sr = Series(data)
    df = cudf.DataFrame(sr)

    got = (sr**2).sum()
    got_df = (df**2).sum()
    expect = (data**2).sum()

    if cudf.dtype(dtype).kind in {"u", "i"}:
        if 0 <= expect <= np.iinfo(dtype).max:
            np.testing.assert_array_almost_equal(expect, got)
            np.testing.assert_array_almost_equal(expect, got_df.iloc[0])
        else:
            print("overflow, passing")
    else:
        np.testing.assert_approx_equal(
            expect, got, significant=accuracy_for_dtype[dtype]
        )
        np.testing.assert_approx_equal(
            expect, got_df.iloc[0], significant=accuracy_for_dtype[dtype]
        )


@pytest.mark.parametrize(
    "dtype",
    [
        Decimal64Dtype(6, 2),
        Decimal64Dtype(8, 4),
        Decimal64Dtype(10, 5),
        Decimal128Dtype(20, 7),
        Decimal32Dtype(6, 2),
    ],
)
def test_sum_of_squares_decimal(dtype):
    np.random.seed(0)
    data = [str(x) for x in gen_rand("int8", 3) / 10]

    expected = pd.Series([Decimal(x) for x in data]).pow(2).sum()
    got = (cudf.Series(data).astype(dtype) ** 2).sum()

    assert_eq(expected, got)


@pytest.mark.parametrize("dtype,nelem", params)
def test_min(dtype, nelem):
    dtype = cudf.dtype(dtype).type
    data = gen_rand(dtype, nelem)
    sr = Series(data)

    got = sr.min()
    expect = dtype(data.min())

    assert expect == got


@pytest.mark.parametrize(
    "dtype",
    [
        Decimal64Dtype(6, 3),
        Decimal64Dtype(10, 6),
        Decimal64Dtype(16, 7),
        Decimal32Dtype(6, 3),
        Decimal128Dtype(20, 7),
    ],
)
@pytest.mark.parametrize("nelem", params_sizes)
def test_min_decimal(dtype, nelem):
    np.random.seed(0)
    data = [str(x) for x in gen_rand("int64", nelem) / 100]

    expected = pd.Series([Decimal(x) for x in data]).min()
    got = cudf.Series(data).astype(dtype).min()

    assert_eq(expected, got)


@pytest.mark.parametrize("dtype,nelem", params)
def test_max(dtype, nelem):
    dtype = cudf.dtype(dtype).type
    data = gen_rand(dtype, nelem)
    sr = Series(data)

    got = sr.max()
    expect = dtype(data.max())

    assert expect == got


@pytest.mark.parametrize(
    "dtype",
    [
        Decimal64Dtype(6, 3),
        Decimal64Dtype(10, 6),
        Decimal64Dtype(16, 7),
        Decimal32Dtype(6, 3),
        Decimal128Dtype(20, 7),
    ],
)
@pytest.mark.parametrize("nelem", params_sizes)
def test_max_decimal(dtype, nelem):
    np.random.seed(0)
    data = [str(x) for x in gen_rand("int64", nelem) / 100]

    expected = pd.Series([Decimal(x) for x in data]).max()
    got = cudf.Series(data).astype(dtype).max()

    assert_eq(expected, got)


@pytest.mark.parametrize("nelem", params_sizes)
def test_sum_masked(nelem):
    dtype = np.float64
    data = gen_rand(dtype, nelem)

    mask = utils.random_bitmask(nelem)
    bitmask = utils.expand_bits_to_bytes(mask)[:nelem]
    null_count = utils.count_zero(bitmask)

    sr = Series.from_masked_array(data, mask, null_count)

    got = sr.sum()
    res_mask = np.asarray(bitmask, dtype=np.bool_)[: data.size]
    expect = data[res_mask].sum()

    significant = 4 if dtype == np.float32 else 6
    np.testing.assert_approx_equal(expect, got, significant=significant)


def test_sum_boolean():
    s = Series(np.arange(100000))
    got = (s > 1).sum(dtype=np.int32)
    expect = 99998

    assert expect == got

    got = (s > 1).sum(dtype=np.bool_)
    expect = True

    assert expect == got


def test_date_minmax():
    np_data = np.random.normal(size=10**3)
    gdf_data = Series(np_data)

    np_casted = np_data.astype("datetime64[ms]")
    gdf_casted = gdf_data.astype("datetime64[ms]")

    np_min = np_casted.min()
    gdf_min = gdf_casted.min()
    assert np_min == gdf_min

    np_max = np_casted.max()
    gdf_max = gdf_casted.max()
    assert np_max == gdf_max


@pytest.mark.parametrize(
    "op",
    ["sum", "product", "var", "kurt", "kurtosis", "skew"],
)
def test_datetime_unsupported_reductions(op):
    gsr = cudf.Series([1, 2, 3, None], dtype="datetime64[ns]")
    psr = gsr.to_pandas()

    utils.assert_exceptions_equal(
        lfunc=getattr(psr, op),
        rfunc=getattr(gsr, op),
    )


@pytest.mark.parametrize("op", ["product", "var", "kurt", "kurtosis", "skew"])
def test_timedelta_unsupported_reductions(op):
    gsr = cudf.Series([1, 2, 3, None], dtype="timedelta64[ns]")
    psr = gsr.to_pandas()

    utils.assert_exceptions_equal(
        lfunc=getattr(psr, op),
        rfunc=getattr(gsr, op),
    )


@pytest.mark.parametrize("op", ["sum", "product", "std", "var"])
def test_categorical_reductions(op):
    gsr = cudf.Series([1, 2, 3, None], dtype="category")
    psr = gsr.to_pandas()

    utils.assert_exceptions_equal(getattr(psr, op), getattr(gsr, op))


@pytest.mark.parametrize(
    "data",
    [
        {"a": [1, 2, 3], "b": [10, 11, 12]},
        {"a": [1, 0, 3], "b": [10, 11, 12]},
        {"a": [1, 2, 3], "b": [10, 11, None]},
        {
            "a": [],
        },
        {},
    ],
)
@pytest.mark.parametrize("op", ["all", "any"])
def test_any_all_axis_none(data, op):
    gdf = cudf.DataFrame(data)
    pdf = gdf.to_pandas()

    expected = getattr(pdf, op)(axis=None)
    actual = getattr(gdf, op)(axis=None)

    assert expected == actual


@pytest.mark.parametrize(
    "op",
    [
        "sum",
        "product",
        "std",
        "var",
        "kurt",
        "kurtosis",
        "skew",
        "min",
        "max",
        "mean",
        "median",
    ],
)
def test_reductions_axis_none_warning(op):
    df = cudf.DataFrame({"a": [1, 2, 3], "b": [10, 2, 3]})
    pdf = df.to_pandas()
    with expect_warning_if(
        op in {"sum", "product", "std", "var"},
        FutureWarning,
    ):
        actual = getattr(df, op)(axis=None)
    with expect_warning_if(
        op in {"sum", "product", "std", "var"},
        FutureWarning,
    ):
        expected = getattr(pdf, op)(axis=None)
    assert_eq(expected, actual, check_dtype=False)
