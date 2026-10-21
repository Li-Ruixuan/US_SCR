"""
Drop-in replacement for the three pytorch3d.transforms functions the TUS-REC baseline uses,
so pytorch3d does not need to be installed. Same conventions as pytorch3d: Euler angles
compose as R = R_axis0(a0) @ R_axis1(a1) @ R_axis2(a2) (e.g. 'ZYX'); quaternions are real-first
(w, x, y, z). Pure PyTorch, differentiable, any leading batch shape.

Use, either:
  * copy the folder pytorch3d/ into the baseline repo root (import pytorch3d.transforms then works), or
  * copy this file to <baseline>/utils/rot.py and in utils/transform.py replace
        import pytorch3d.transforms
    by
        from utils import rot as _rot
        class pytorch3d:
            transforms = _rot
"""

import torch


def _axis_angle_rotation(axis: str, angle: torch.Tensor) -> torch.Tensor:
    c, s = torch.cos(angle), torch.sin(angle)
    one, zero = torch.ones_like(angle), torch.zeros_like(angle)
    if axis == "X":
        flat = (one, zero, zero, zero, c, -s, zero, s, c)
    elif axis == "Y":
        flat = (c, zero, s, zero, one, zero, -s, zero, c)
    elif axis == "Z":
        flat = (c, -s, zero, s, c, zero, zero, zero, one)
    else:
        raise ValueError(f"letter must be X, Y or Z, got {axis}")
    return torch.stack(flat, -1).reshape(angle.shape + (3, 3))


def euler_angles_to_matrix(euler_angles: torch.Tensor, convention: str) -> torch.Tensor:
    if euler_angles.shape[-1] != 3 or len(convention) != 3:
        raise ValueError("need 3 angles and a 3-letter convention")
    m = [_axis_angle_rotation(c, e) for c, e in zip(convention, torch.unbind(euler_angles, -1))]
    return m[0] @ m[1] @ m[2]


def _index_from_letter(letter: str) -> int:
    return {"X": 0, "Y": 1, "Z": 2}[letter]


def _angle_from_tan(axis, other_axis, data, horizontal, tait_bryan):
    i1, i2 = {"X": (2, 1), "Y": (0, 2), "Z": (1, 0)}[axis]
    if horizontal:
        i2, i1 = i1, i2
    even = (axis + other_axis) in ["XY", "YZ", "ZX"]
    if horizontal == even:
        return torch.atan2(data[..., i1], data[..., i2])
    if tait_bryan:
        return torch.atan2(-data[..., i2], data[..., i1])
    return torch.atan2(data[..., i2], -data[..., i1])


def matrix_to_euler_angles(matrix: torch.Tensor, convention: str) -> torch.Tensor:
    if matrix.shape[-2:] != (3, 3) or len(convention) != 3:
        raise ValueError("need (..., 3, 3) matrices and a 3-letter convention")
    i0, i2 = _index_from_letter(convention[0]), _index_from_letter(convention[2])
    tait_bryan = i0 != i2
    if tait_bryan:
        central = torch.asin(matrix[..., i0, i2] * (-1.0 if i0 - i2 in [-1, 2] else 1.0))
    else:
        central = torch.acos(matrix[..., i0, i0])
    return torch.stack((
        _angle_from_tan(convention[0], convention[1], matrix[..., i2], False, tait_bryan),
        central,
        _angle_from_tan(convention[2], convention[1], matrix[..., i0, :], True, tait_bryan)), -1)


def quaternion_to_matrix(quaternions: torch.Tensor) -> torch.Tensor:
    r, i, j, k = torch.unbind(quaternions, -1)
    two_s = 2.0 / (quaternions * quaternions).sum(-1)
    o = torch.stack((
        1 - two_s * (j * j + k * k), two_s * (i * j - k * r), two_s * (i * k + j * r),
        two_s * (i * j + k * r), 1 - two_s * (i * i + k * k), two_s * (j * k - i * r),
        two_s * (i * k - j * r), two_s * (j * k + i * r), 1 - two_s * (i * i + j * j)), -1)
    return o.reshape(quaternions.shape[:-1] + (3, 3))
