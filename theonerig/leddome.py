# AUTOGENERATED! DO NOT EDIT! File to edit: 13_leddome.ipynb (unless otherwise specified).

__all__ = ['get_dome_positions', 'as_cartesian', 'as_spherical', 'angular_distance', 'build_wave_stimulus_array',
           'Quaternion', 'get_waves_relative_position', 'get_led_relative_position']

# Cell
import numpy as np
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Cell
def get_dome_positions(mode="cartesian"):
    """
    Generates positions of all LEDs of the dome. Position of first and last LED of each stripe
    were estimated in Blender, and other in between LEDs position are interpolated from those two.

    params:
        - mode: What coordinates to obtain in set ["cartesian", "spherical"]
    return:
        - LED position of the LED dome, in shape (4, 237). shape[0] organized by quarter (q1 to q4) and shape[1] is the
        concatenation of (left,right)
    """
    assert mode in ["cartesian", "spherical"], """Mode must be one of ["cartesian", "spherical"]"""
    stripe_dict = {}
    stripe = np.array([[-0.44162,0.46045,10.07932], [-0.03378,10.07122,0.72211]])*10
    stripe_dict["A"] = _slerp(stripe, 23)

    stripe = np.array([[0.42254,1.33094,10.00507], [0.83062,9.99418,1.12168]])*10
    stripe_dict["B"] = _slerp(stripe, 21)

    stripe = np.array([[-1.3044,1.33575,9.94323], [-0.93444, 10.00996,0.99274]])*10
    stripe_dict["C"] = _slerp(stripe, 21)

    stripe = np.array([[1.35075,2.2321,9.75535], [1.68846,9.91944,0.77928]])*10
    stripe_dict["D"] = _slerp(stripe, 20)

    stripe = np.array([[-2.20708,2.29345,9.58381], [-1.8337,9.92046,1.14081]])*10
    stripe_dict["E"] = _slerp(stripe, 19)

    stripe = np.array([[2.31814,3.13993,9.31365], [2.52401,9.74959,0.86306]])*10
    stripe_dict["F"] = _slerp(stripe, 18)

    stripe = np.array([[-3.15667,3.31007,9.00523], [-2.69219,9.68376,1.0918]])*10
    stripe_dict["G"] = _slerp(stripe, 17)

    stripe = np.array([[3.3186,4.12493,8.60008], [3.28828,9.52856,0.61278]])*10
    stripe_dict["H"] = _slerp(stripe, 16)

    stripe = np.array([[-4.0779,4.27888,8.18478], [-3.45295,9.45243,0.77226]])*10
    stripe_dict["I"] = _slerp(stripe, 15)

    stripe = np.array([[4.29328,5.00709,7.63564], [4.17924,9.14635,1.03659]])*10
    stripe_dict["J"] = _slerp(stripe, 13)

    stripe = np.array([[-4.99026,5.24451,7.06361], [-4.3501,9.07599,1.00064]])*10
    stripe_dict["K"] = _slerp(stripe, 12)

    stripe = np.array([[5.22638,5.86208,6.3335], [4.85207,8.84847,0.57339]])*10
    stripe_dict["L"] = _slerp(stripe, 11)

    stripe = np.array([[-5.77797,6.10141,5.60405], [-5.14097,8.63676,1.02421]])*10
    stripe_dict["M"] = _slerp(stripe, 9)

    stripe = np.array([[6.03059,6.57628,4.71668], [5.55174,8.42348,0.46679]])*10
    stripe_dict["N"] = _slerp(stripe, 8)

    stripe = np.array([[-6.40277,6.82204,3.80993], [-5.84937,8.19519,0.84915]])*10
    stripe_dict["O"] = _slerp(stripe, 6)

    stripe = np.array([[6.62294,7.08816,2.77088], [6.34649,7.81552,0.85683]])*10
    stripe_dict["P"] = _slerp(stripe, 4)

    stripe = np.array([[-6.77734,7.27747,1.7878], [-6.49463,7.71771,0.6162]])*10
    stripe_dict["Q"] = _slerp(stripe, 3)

    stripe = np.array([[6.94329,7.30411,0.65871]])*10
    stripe_dict["R"] = stripe

    res = _symetry_stripes(_chain_stripes(stripe_dict))
    if mode=="spherical":
        res = np.apply_along_axis(as_spherical, axis=-1, arr=res)
    return res

def _symetry_stripes(stripe):
    """
    Generates the 90° symetry of three stripes from the given stripe.
    """
    all_stripes = np.stack([stripe]*4, axis=0)
    tmp = all_stripes[1,:,0]*-1
    all_stripes[1,:,0] = all_stripes[1,:,1]
    all_stripes[1,:,1] = tmp

    all_stripes[2,:,0] *= -1
    all_stripes[2,:,1] *= -1

    tmp = all_stripes[3,:,1]*-1
    all_stripes[3,:,1] = all_stripes[3,:,0]
    all_stripes[3,:,0] = tmp
    return all_stripes

def _slerp(leds_xyz, n_led):
    """Interpolate positions from the xyz positon of the first and last LED

    params:
        -leds_xyz: np.array of shape(2,3)
        -n_led: total n LED on the stripe
    return:
        - interpolated positions
    """
    p0, p1 = leds_xyz[0], leds_xyz[1]

    omega = math.acos(np.dot(p0/np.linalg.norm(p0), p1/np.linalg.norm(p1)))
    so = math.sin(omega)
    return [math.sin((1.0-t)*omega) / so * p0 + math.sin(t*omega)/so * p1 for t in np.linspace(0.0, 1.0, n_led)]

def as_cartesian(rthetaphi, is_radian=True):
    """
    Convert 3D polar coordinate tuple into cartesian coordinates.

    params:
        - rthetaphi: Single or list of (r, theta, phi) iterable
        - is_radian: Boolean to specify if in radians or in degrees
    return:
        - Single or list of converted (x, y, z) array.
    """
    r, theta, phi = tuple(np.array(rthetaphi).T)
    if not is_radian:
        theta   = theta*np.pi/180
        phi     = phi*np.pi/180
    x = r * np.sin( theta ) * np.cos( phi )
    y = r * np.sin( theta ) * np.sin( phi )
    z = r * np.cos( theta )
    return np.stack([x,y,z], axis=-1)

def as_spherical(xyz):
    """
    Convert 3D cartesian coordinates tuple into polar coordinate.

    params:
        - xyz: Single or list of (x, y, z) iterable
    return:
        - Single or list of converted (r, theta, phi) array.
    """
    x, y, z = tuple(np.array(xyz).T)
    r       =  np.sqrt(x*x + y*y + z*z)
    theta   =  np.arccos(z/r)
    phi     =  np.arctan2(y,x)
    return np.stack([r,theta,phi], axis=-1)

def angular_distance(theta_1, phi_1, theta_2, phi_2):
    """
    Computes the angle separating two points (or a list of points) on a sphere, in radians.
    params:
        - theta_1: Theta angle of the first point.
        - phi_1:   Phi angle of the first point.
        - theta_2: Theta angle of the second point.
        - phi_2:   Phi angle of the second point.
    """
    theta_1 = (np.pi/2)-theta_1 #The formula works for Declination angle
    theta_2 = (np.pi/2)-theta_2

    return np.arccos(np.sin(theta_1)*np.sin(theta_2) +
                     np.cos(theta_1)*np.cos(theta_2)*np.cos(phi_2-phi_1))

def _chain_stripes(stripe_dict):
    """
    Chain the stripes to create a one-dimensional array were LED idx correspond to their index on the stripe,
    with left side first.
    """
    res = []
    UP,DOWN = -1,1
    ori = UP
    left_side = ["B","D","F","H","J","L","N","P","R"]
    for key in left_side:
        res.extend(stripe_dict[key][::ori])
        ori *= -1

    ori = UP
    right_side = ["Q","O","M","K","I","G","E","C","A"]
    for key in right_side:
        res.extend(stripe_dict[key][::ori])
        ori *= -1
    return np.array(res)

# Cell
def build_wave_stimulus_array(epoch_sequence, wave_width=0.58, wave_speed=.58, n_frame_epoch=640, n_frame_isi=50, frame_rate=100):
    """
    Build the numpy stimulus matrix of the LED values for each frame.
    params:
        - epoch_sequence: Sequence of indexes played randomly during the stimulation
        - wave_width: Width of the wave in radians
        - wave_speed: Speed of the wave in radians.s-1
        - n_frame_epoch: Number of frames that an epoch last
        - n_frame_isi: Number of frames during teh inter-stimulus-interval
        - frame_rate: Frame rate of the display
    returns:
        - LED values for the wave stimulus, in shape (t, 4, 237), where t=n_epoch*(n_frame_epoch+n_frame_isi)
    """
    n_epoch = np.max(epoch_sequence)+1

    polar_pos  = get_dome_positions(mode="spherical") #r, theta, phi
    theta_leds = polar_pos[:,:,1].reshape(-1)
    phi_leds   = polar_pos[:,:,2].reshape(-1)

    indexes  = np.arange(n_epoch)+0.5
    #Theta and phi make the axis around which the LEDs are rotated by alpha
    theta    = np.pi/2; #Theta is fixed, corresponds to the plane touching the dome edge (elevation=0° or inclination=90°)
    phis     = np.pi*(1 + np.sqrt(5)) * indexes #Angle of rotation around the centre
    alphas   = np.arccos(1 - 2*indexes/n_epoch)     #Distance angle from the centre

    tmp  = np.sin(0.5*alphas)
    qA_0 = np.cos(0.5*alphas)[:, None] #Quaternion of the rotation. Adding axis to do matrix multiplication
    qA_x = (np.sin(theta)*np.cos(phis)*tmp)[:, None]
    qA_y = (np.sin(theta)*np.sin(phis)*tmp)[:, None]
    qA_z = (np.cos(theta)         *tmp)[:, None]

    qB_x_leds = (np.sin(theta_leds)*np.cos(phi_leds))[:, None].T
    qB_y_leds = (np.sin(theta_leds)*np.sin(phi_leds))[:, None].T
    qB_z_leds = (np.cos(theta_leds))[:, None].T

    #Computes each LED elevation for each rotation. Involve Quaternions. Only the relevant values are calculated
    mq0 = -(qA_x@qB_x_leds) - (qA_y@qB_y_leds) - (qA_z@qB_z_leds)
    mqx =  (qA_0@qB_x_leds) + (qA_y@qB_z_leds) - (qA_z@qB_y_leds)
    mqy =  (qA_0@qB_y_leds) - (qA_x@qB_z_leds) + (qA_z@qB_x_leds)
    mqz =  (qA_0@qB_z_leds) + (qA_x@qB_y_leds) - (qA_y@qB_x_leds)

    mqz = (mq0 * (-qA_z)) + (mqx * (-qA_y)) - (mqy * (-qA_x)) + (mqz * qA_0)

    LED_elevations = np.arccos(mqz)
    LED_elevations = LED_elevations[epoch_sequence]

    frame_step      = wave_speed/frame_rate
    wave_elevations = np.arange(n_frame_epoch)*frame_step #Building the values used to compare the LED_elevation with

    time_shape = n_epoch*(n_frame_epoch+n_frame_isi)
    result     = np.empty((time_shape, *theta_leds.shape))
    for i, LED_elevation in enumerate(LED_elevations):
        for j, wave_elevation in enumerate(wave_elevations):
            result[i*(n_frame_epoch+n_frame_isi)+j] = (wave_elevation-wave_width<LED_elevation) & (LED_elevation<wave_elevation)
    return result.reshape(time_shape,4, -1)

# Cell
class Quaternion( object ):
    """
    Simplified Quaternion class for rotation of normalized vectors only!
    """

    def __init__( self, q0, qx, qy, qz ):
        """
        Internally uses floats to avoid integer division issues.

        @param q0: int or float
        @param qx: int or float
        @param qy: int or float
        @param qz: int or float
        """
        self._q0 = float( q0 )
        self._qx = float( qx )
        self._qy = float( qy )
        self._qz = float( qz )
        """
        Note if interpreted as rotation q0 -> -q0 doesn't make a difference
        q0 = cos( w ) so -cos( w ) = cos( w + pi ) and as the rotation
        is by twice the angle it is either 2w or 2w + 2pi, the latter being equivalent to the former.
        """

    def conjugate(q):
        """
        @return Quaternion
        """
        conjq = Quaternion( q._q0, -q._qx, -q._qy, -q._qz )
        return conjq

    def __mul__(q, r):
        """
        Non commutative quaternion multiplication.
        @return Quaternion
        """
        if isinstance(r, Quaternion):
            mq0 = q._q0 * r._q0 - q._qx * r._qx - q._qy * r._qy - q._qz * r._qz
            mqx = q._q0 * r._qx + q._qx * r._q0 + q._qy * r._qz - q._qz * r._qy
            mqy = q._q0 * r._qy - q._qx * r._qz + q._qy * r._q0 + q._qz * r._qx
            mqz = q._q0 * r._qz + q._qx * r._qy - q._qy * r._qx + q._qz * r._q0
            out = Quaternion(mq0, mqx, mqy, mqz)
        else:
            raise TypeError
        return out

    def __getitem__( q, idx ):
        """
        @return float
        """
        if idx < 0:
            idx = 4 + idx
        if idx in [ 0, 1, 2, 3 ]:
            out = (q._q0, q._qx, q._qy, q._qz)[idx]
        else:
            raise IndexError
        return out

# Cell
def get_waves_relative_position(cell_sta_position, n_waves=100, mode="spherical"):
    """
    Rotate the waves origins to obtain for the ref_led_flat_idx a spherical position of (0,0)
    params:
        - cell_sta_position: (theta, phi) Tuple of the cell position in spherical coordinates
        - n_waves: Number of waves in the wave stimulus (positions/density of waves determined by this parameter)
        - mode: One of ["spherical", "cartesian"], for the returned position
    return:
        - The rotated waves position
    """
    assert mode in ["spherical", "cartesian"], 'Mode must be one of ["spherical", "cartesian"]'

    theta_led = cell_sta_position[0]
    phi_led   = cell_sta_position[1]

    #Creation of the rotation quaternion and it's conjugate
    theta_rot    = np.pi/2; #Theta is fixed, corresponds to the plane touching the dome edge (elevation=0°)
    phi_rot      = phi_led+np.pi/2
    alpha_rot    = -theta_led

    xA, yA, zA = np.sin(theta_rot)*np.cos(phi_rot), np.sin(theta_rot)*np.sin(phi_rot), np.cos(theta_rot)
    tmp        = np.sin(0.5*alpha_rot)
    rot_quat   = Quaternion(np.cos(0.5*alpha_rot), xA*tmp, yA*tmp, zA*tmp)
    rot_conj   = rot_quat.conjugate()

    #Creation of the wave quaternions
    indexes       = np.arange(n_waves)+0.5
    phis_wave     = np.pi*(1 + np.sqrt(5)) * indexes + np.pi/2  #Angle of rotation around the centre. Add pi/2 to correspond to the displayed wave positon
    theta_wave    = np.arccos(1 - 2*indexes/n_waves)  #Distance angle from the centre
    xB, yB, zB = np.sin(theta_wave)*np.cos(phis_wave), np.sin(theta_wave)*np.sin(phis_wave), np.cos(theta_wave)
    quaternions_wave = [Quaternion(0,x,y,z) for x,y,z in zip(xB, yB, zB)]

    #Rotation of the waves
    rotated_waves      = [rot_quat*(q*rot_conj) for q in quaternions_wave]
    if mode=="spherical":
        return np.array([as_spherical((q[1], q[2], q[3])) for q in rotated_waves])
    else:
        return np.array([(q[1], q[2], q[3]) for q in rotated_waves])

def get_led_relative_position(ref_led_flat_idx, mode="spherical"):
    """
    Rotate the LED positions to obtain for the ref_led_flat_idx a spherical position of (0,0)
    params:
        - ref_led_flat_idx: Flattened index of the reference LED (e.g. obtained with np.argmax on abs STA values)
        - mode: One of ["spherical", "cartesian"], for the returned position
    return:
        - The rotated LED position
    """
    assert mode in ["spherical", "cartesian"], 'Mode must be one of ["spherical", "cartesian"]'

    theta_led = get_dome_positions(mode="spherical")[ref_led_flat_idx//237,ref_led_flat_idx%237,1]
    phi_led   = get_dome_positions(mode="spherical")[ref_led_flat_idx//237,ref_led_flat_idx%237,2]

    #Creation of the rotation quaternion and it's conjugate
    theta_rot    = np.pi/2; #Theta is fixed, corresponds to the plane touching the dome edge (elevation=0°)
    phi_rot      = phi_led+np.pi/2
    alpha_rot    = -theta_led

    xA, yA, zA = np.sin(theta_rot)*np.cos(phi_rot), np.sin(theta_rot)*np.sin(phi_rot), np.cos(theta_rot)
    tmp        = np.sin(0.5*alpha_rot)
    rot_quat   = Quaternion(np.cos(0.5*alpha_rot), xA*tmp, yA*tmp, zA*tmp)
    rot_conj   = rot_quat.conjugate()

    cart_pos  = get_dome_positions(mode="cartesian") #r, theta, phi
    x_leds = cart_pos[:,:,0].reshape(-1)
    y_leds = cart_pos[:,:,1].reshape(-1)
    z_leds = cart_pos[:,:,2].reshape(-1)

    quaternions_leds = [Quaternion(0,x,y,z) for x,y,z in zip(x_leds, y_leds, z_leds)]
    rotated_leds     = [rot_quat*(q*rot_conj) for q in quaternions_leds]
    if mode=="spherical":
        relative_led_pos = np.array([as_spherical((q[1], q[2], q[3])) for q in rotated_leds])
    else:
        relative_led_pos = np.array([(q[1], q[2], q[3]) for q in rotated_leds])

    return relative_led_pos