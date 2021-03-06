from ncachefactory.arrayutils import range_ranges, compute_wedging_values, overlap_arrays_from_ranges, normalize_ranges, global_ranges


def test_range_ranges():
    assert range_ranges([0, 10], [5, 15]) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15] == global_ranges([0, 10], [5, 15])
    assert range_ranges([0, 5], [10, 15]) == [0, 1, 2, 3, 4, 5, 10, 11, 12, 13, 14, 15] == global_ranges(([0, 5], [10, 15])
    assert range_ranges([5, 15], [0, 10]) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15] == global_ranges([5, 15], [0, 10])
    assert range_ranges([10, 15], [0, 5]) == [0, 1, 2, 3, 4, 5, 10, 11, 12, 13, 14, 15] == global_ranges([10, 15], [0, 5])
    assert range_ranges([5, 15], [0, 10]) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15] == global_ranges([5, 15], [0, 10])
    assert range_ranges([10, 15], [0, 5]) == [0, 1, 2, 3, 4, 5, 10, 11, 12, 13, 14, 15] == global_ranges([10, 15], [0, 5])


def test_normalize_ranges():
    assert normalize_ranges([50, 100], [50, 100]) == [[0, 50], [0, 50]]
    assert normalize_ranges([50, 100], [70, 120]) == [[0, 50], [20, 70]]
    assert normalize_ranges([50, 90], [100, 110]) == [[0, 40], [41, 51]]
    assert normalize_ranges([100, 110], [50, 90]) == [[41, 51], [0, 40]]
    assert normalize_ranges([20, 40], [50, 65]) == [[0, 20], [21, 36]]
    assert normalize_ranges([50, 65], [20, 40]) == [[21, 36], [0, 20]]
    assert normalize_ranges([0, 100], [20, 40]) == [[0, 100], [20, 40]]
    assert normalize_ranges([50, 150], [70, 90]) == [[0, 100], [20, 40]]
    assert normalize_ranges([20, 40], [0, 100]) == [[20, 40], [0, 100]]
    assert normalize_ranges([70, 90], [50, 150]) == [[20, 40], [0, 100]]


def test_overlap_list_from_ranges():
    range1 = [20, 40]
    range2 = [50, 65]
    elements1 = [True for _ in range(range1[0], range1[1] + 1)]
    elements2 = [True for _ in range(range2[0], range2[1] + 1)]
    result = overlap_arrays_from_ranges(elements1, elements2, range1, range2)
    assert result == [[
        True, True, True, True, True, True, True, True, True, True, True, True,
        True, True, True, True, True, True, True, True, True, None, None, None,
        None, None, None, None, None, None, None, None, None, None, None, None],[
        None, None, None, None, None, None, None, None, None, None, None, None,
        None, None, None, None, None, None, None, None, None, True, True, True,
        True, True, True, True, True, True, True, True, True, True, True, True]]


def test_compute_wedging_values():
    assert compute_wedging_values(0, 1, 2) == (0, 1)
    assert compute_wedging_values(1, 2, 2) == (1, 2)
    assert compute_wedging_values(-1, 2, 2) == (-1, 2)
    assert compute_wedging_values(1, 2, 2) == (1, 2)
    assert compute_wedging_values(-1, 1, 3) == [-1, 0, 1]
    assert len(compute_wedging_values(1, 2, 10)) == 10


if __name__ == "__main__":
    test_range_ranges()
    test_compute_wedging_values()
    test_overlap_list_from_ranges()
    test_normalize_ranges()