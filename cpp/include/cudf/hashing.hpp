/*
 * Copyright (c) 2019-2024, NVIDIA CORPORATION.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
#pragma once

#include <cudf/table/table.hpp>
#include <cudf/table/table_view.hpp>

#include <rmm/mr/device/per_device_resource.hpp>

namespace cudf {

/**
 * @addtogroup column_hash
 * @{
 * @file
 */

/**
 * @brief Type of hash value
 *
 */
using hash_value_type = uint32_t;

/**
 * @brief Identifies the hash function to be used
 *
 */
enum class hash_id {
  HASH_IDENTITY = 0,   ///< Identity hash function that simply returns the key to be hashed
  HASH_MURMUR3,        ///< Murmur3 hash function
  HASH_SPARK_MURMUR3,  ///< Spark Murmur3 hash function
  HASH_MD5             ///< MD5 hash function
};

/**
 * @brief The default seed value for hash functions
 */
static constexpr uint32_t DEFAULT_HASH_SEED = 0;

/**
 * @brief Computes the hash value of each row in the input set of columns.
 *
 * @deprecated Since 23.08
 *
 * @param input The table of columns to hash
 * @param hash_function The hash function enum to use
 * @param seed Optional seed value to use for the hash function
 * @param stream CUDA stream used for device memory operations and kernel launches
 * @param mr Device memory resource used to allocate the returned column's device memory
 *
 * @returns A column where each row is the hash of a column from the input
 */
std::unique_ptr<column> hash(
  table_view const& input,
  hash_id hash_function               = hash_id::HASH_MURMUR3,
  uint32_t seed                       = DEFAULT_HASH_SEED,
  rmm::cuda_stream_view stream        = cudf::get_default_stream(),
  rmm::mr::device_memory_resource* mr = rmm::mr::get_current_device_resource());

//! Hash APIs
namespace hashing {

/**
 * @brief Computes the MurmurHash3 32-bit hash value of each row in the given table
 *
 * This function computes the hash of each column using the `seed` for the first column
 * and the resulting hash as a seed for the next column and so on.
 * The result is a uint32 value for each row.
 *
 * @param input The table of columns to hash
 * @param seed Optional seed value to use for the hash function
 * @param stream CUDA stream used for device memory operations and kernel launches
 * @param mr Device memory resource used to allocate the returned column's device memory
 *
 * @returns A column where each row is the hash of a row from the input
 */
std::unique_ptr<column> murmurhash3_x86_32(
  table_view const& input,
  uint32_t seed                       = DEFAULT_HASH_SEED,
  rmm::cuda_stream_view stream        = cudf::get_default_stream(),
  rmm::mr::device_memory_resource* mr = rmm::mr::get_current_device_resource());

/**
 * @brief Computes the MurmurHash3 64-bit hash value of each row in the given table
 *
 * This function takes a 64-bit seed value and returns hash values using the
 * MurmurHash3_x64_128 algorithm. The hash produces in two uint64 values per row.
 *
 * @param input The table of columns to hash
 * @param seed Optional seed value to use for the hash function
 * @param stream CUDA stream used for device memory operations and kernel launches
 * @param mr Device memory resource used to allocate the returned column's device memory
 *
 * @returns A table of two UINT64 columns
 */
std::unique_ptr<table> murmurhash3_x64_128(
  table_view const& input,
  uint64_t seed                       = DEFAULT_HASH_SEED,
  rmm::cuda_stream_view stream        = cudf::get_default_stream(),
  rmm::mr::device_memory_resource* mr = rmm::mr::get_current_device_resource());

/**
 * @brief Computes the MurmurHash3 32-bit hash value of each row in the given table
 *
 * This function computes the hash similar to MurmurHash3_x86_32 with special processing
 * to match Spark's implementation results.
 *
 * @param input The table of columns to hash
 * @param seed Optional seed value to use for the hash function
 * @param stream CUDA stream used for device memory operations and kernel launches
 * @param mr Device memory resource used to allocate the returned column's device memory
 *
 * @returns A column where each row is the hash of a row from the input
 */
std::unique_ptr<column> spark_murmurhash3_x86_32(
  table_view const& input,
  uint32_t seed                       = DEFAULT_HASH_SEED,
  rmm::cuda_stream_view stream        = cudf::get_default_stream(),
  rmm::mr::device_memory_resource* mr = rmm::mr::get_current_device_resource());

/**
 * @brief Computes the MD5 hash value of each row in the given table
 *
 * @param input The table of columns to hash
 * @param stream CUDA stream used for device memory operations and kernel launches
 * @param mr Device memory resource used to allocate the returned column's device memory
 *
 * @returns A column where each row is the hash of a row from the input
 */
std::unique_ptr<column> md5(
  table_view const& input,
  rmm::cuda_stream_view stream        = cudf::get_default_stream(),
  rmm::mr::device_memory_resource* mr = rmm::mr::get_current_device_resource());

/**
 * @brief Computes the SHA-1 hash value of each row in the given table
 *
 * @param input The table of columns to hash
 * @param stream CUDA stream used for device memory operations and kernel launches
 * @param mr Device memory resource used to allocate the returned column's device memory
 *
 * @returns A column where each row is the hash of a row from the input
 */
std::unique_ptr<column> sha1(
  table_view const& input,
  rmm::cuda_stream_view stream        = cudf::get_default_stream(),
  rmm::mr::device_memory_resource* mr = rmm::mr::get_current_device_resource());

/**
 * @brief Computes the SHA-224 hash value of each row in the given table
 *
 * @param input The table of columns to hash
 * @param stream CUDA stream used for device memory operations and kernel launches
 * @param mr Device memory resource used to allocate the returned column's device memory
 *
 * @returns A column where each row is the hash of a row from the input
 */
std::unique_ptr<column> sha224(
  table_view const& input,
  rmm::cuda_stream_view stream        = cudf::get_default_stream(),
  rmm::mr::device_memory_resource* mr = rmm::mr::get_current_device_resource());

/**
 * @brief Computes the SHA-256 hash value of each row in the given table
 *
 * @param input The table of columns to hash
 * @param stream CUDA stream used for device memory operations and kernel launches
 * @param mr Device memory resource used to allocate the returned column's device memory
 *
 * @returns A column where each row is the hash of a row from the input
 */
std::unique_ptr<column> sha256(
  table_view const& input,
  rmm::cuda_stream_view stream        = cudf::get_default_stream(),
  rmm::mr::device_memory_resource* mr = rmm::mr::get_current_device_resource());

/**
 * @brief Computes the SHA-384 hash value of each row in the given table
 *
 * @param input The table of columns to hash
 * @param stream CUDA stream used for device memory operations and kernel launches
 * @param mr Device memory resource used to allocate the returned column's device memory
 *
 * @returns A column where each row is the hash of a row from the input
 */
std::unique_ptr<column> sha384(
  table_view const& input,
  rmm::cuda_stream_view stream        = cudf::get_default_stream(),
  rmm::mr::device_memory_resource* mr = rmm::mr::get_current_device_resource());

/**
 * @brief Computes the SHA-512 hash value of each row in the given table
 *
 * @param input The table of columns to hash
 * @param stream CUDA stream used for device memory operations and kernel launches
 * @param mr Device memory resource used to allocate the returned column's device memory
 *
 * @returns A column where each row is the hash of a row from the input
 */
std::unique_ptr<column> sha512(
  table_view const& input,
  rmm::cuda_stream_view stream        = cudf::get_default_stream(),
  rmm::mr::device_memory_resource* mr = rmm::mr::get_current_device_resource());

/**
 * @brief Computes the XXHash_64 hash value of each row in the given table
 *
 * This function takes a 64-bit seed value and returns a column of type UINT64.
 *
 * @param input The table of columns to hash
 * @param seed Optional seed value to use for the hash function
 * @param stream CUDA stream used for device memory operations and kernel launches
 * @param mr Device memory resource used to allocate the returned column's device memory
 *
 * @returns A column where each row is the hash of a row from the input
 */
std::unique_ptr<column> xxhash_64(
  table_view const& input,
  uint64_t seed                       = DEFAULT_HASH_SEED,
  rmm::cuda_stream_view stream        = cudf::get_default_stream(),
  rmm::mr::device_memory_resource* mr = rmm::mr::get_current_device_resource());

}  // namespace hashing

/** @} */  // end of group
}  // namespace cudf
