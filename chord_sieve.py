import numpy as np
import time
from numba import njit, prange

@njit(parallel=True, fastmath=True)
def _segmented_vertical_chord_sieve(max_w, max_k, segment_size):
    """
    Parallel segmented vertical chord sieve implementation.
    
    Parameters:
    -----------
    max_w : int
        The maximum index limit, defined as (N - 1) // 2.
    max_k : int
        The maximum chord order, defined as floor((sqrt(2*max_w + 1) - 1) / 2).
    segment_size : int
        Size of each execution segment in memory (optimized for CPU Cache).
        
    Returns:
    --------
    int : Total prime count pi(N).
    """
    # Precompute A(k) and Step(k)
    A = np.empty(max_k + 1, dtype=np.int64)
    step = np.empty(max_k + 1, dtype=np.int64)
    for k in range(1, max_k + 1):
        A[k] = 2 * k * k + 2 * k
        step[k] = 2 * k + 1

    num_segments = (max_w + segment_size) // segment_size
    segment_counts = np.zeros(num_segments, dtype=np.int64)

    # Parallel loop over memory segments
    for seg_idx in prange(num_segments):
        seg_start = seg_idx * segment_size
        seg_end = min(seg_start + segment_size - 1, max_w)
        actual_size = seg_end - seg_start + 1

        # Boolean sieve array for the current segment (True = Prime)
        seg_is_prime = np.ones(actual_size, dtype=np.bool_)

        # Eliminate index 0 (W=0 corresponds to 2W+1=1, which is not prime)
        if seg_start == 0:
            seg_is_prime[0] = False

        # Apply vertical chord scanning for each order k
        for k in range(1, max_k + 1):
            ak = A[k]
            st = step[k]

            if ak > max_w:
                break
            if ak > seg_end:
                continue

            # Calculate first composite entry inside the current segment
            if ak >= seg_start:
                first_w = ak
            else:
                rem = (seg_start - ak) % st
                first_w = seg_start if rem == 0 else seg_start + (st - rem)

            # Mark all composite nodes along the vertical chord vector
            for w in range(first_w, seg_end + 1, st):
                seg_is_prime[w - seg_start] = False

        # Count primes in this segment
        segment_counts[seg_idx] = np.sum(seg_is_prime)

    # Sum all segment results and add 1 for the prime 2
    return np.sum(segment_counts) + 1


def count_primes(N, segment_size=2_000_000):
    """
    Main interface to calculate the prime-counting function pi(N).
    
    Parameters:
    -----------
    N : int
        Upper bound limit for prime counting.
    segment_size : int, optional
        Segment size for CPU cache optimization (default: 2,000,000).
        
    Returns:
    --------
    tuple: (prime_count, elapsed_time_in_seconds)
    """
    if N < 2:
        return 0, 0.0
    if N == 2:
        return 1, 0.0

    max_w = (N - 1) // 2
    max_k = int((np.sqrt(2 * max_w + 1) - 1) / 2)

    start_time = time.perf_counter()
    total_primes = _segmented_vertical_chord_sieve(max_w, max_k, segment_size)
    elapsed = time.perf_counter() - start_time

    return total_primes, elapsed


if __name__ == "__main__":
    import sys
    limit = 1_000_000_000 if len(sys.argv) < 2 else int(sys.argv[1])
    print(f"Computing pi({limit:,})...")
    
    # Warmup JIT
    _, _ = count_primes(100_000)
    
    # Execution
    primes, duration = count_primes(limit)
    print(f"Result: pi({limit:,}) = {primes:,}")
    print(f"Execution Time: {duration:.4f} seconds")