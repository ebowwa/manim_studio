from src.config.manim_config import config
from manim import *
import numpy as np
from scipy.optimize import fsolve, root, root_scalar
from typing import Optional, Union, Dict, List, Tuple, Callable


class CADObject:
    """Base class for CAD-style objects with common properties"""
    
    DEFAULT_CAD_COLOR = "#FF6B6B"  # Technical red
    DEFAULT_STROKE_WIDTH = 2
    DEFAULT_TEXT_COLOR = WHITE
    

# ============= Utility Functions =============

def angle_between_vectors_signed(v1: np.ndarray, v2: np.ndarray) -> float:
    """
    Get signed angle between vectors according to right hand rule.
    
    Args:
        v1: First vector
        v2: Second vector
        
    Returns:
        Angle of rotation that rotates v1 to be co-linear with v2. Range: -PI...+PI
    """
    cval = np.dot(v1, v2)
    sval = (np.cross(v1, v2))[2] if len(v1) >= 3 else np.cross(v1[:2], v2[:2])
    return np.arctan2(sval, cval)


# ============= Corner Modifications =============

class RoundCorners:
    """Utility class for rounding corners of VMobjects"""
    
    @staticmethod
    def round_corner_param(radius: float, curve_points_1: np.ndarray, 
                          curve_points_2: np.ndarray) -> Tuple[Dict, np.ndarray]:
        """Calculate parameters for rounding a corner between two curves"""
        bez_func_1 = bezier(curve_points_1)
        diff_func_1 = bezier((curve_points_1[1:, :] - curve_points_1[:-1, :]) / 3)
        bez_func_2 = bezier(curve_points_2)
        diff_func_2 = bezier((curve_points_2[1:, :] - curve_points_2[:-1, :]) / 3)

        def find_crossing(p1, p2, n1, n2):
            t = fsolve(lambda t: p1[:2] + n1[:2] * t[0] - (p2[:2] + n2[:2] * t[1]), [0, 0])
            return t, p1 + n1 * t[0]

        def rad_cost_func(t):
            angle_sign = np.sign(angle_between_vectors_signed(diff_func_1(t[0]), diff_func_2(t[1])))
            p1 = bez_func_1((t[0]))
            n1 = normalize(rotate_vector(diff_func_1(t[0]), angle_sign * PI / 2))
            p2 = bez_func_2((t[1]))
            n2 = normalize(rotate_vector(diff_func_2(t[1]), angle_sign * PI / 2))
            d = (find_crossing(p1, p2, n1, n2))[0]
            return ((d[0]) - (d[1])), ((d[1]) + (d[0]) - 2 * radius)

        k = root(rad_cost_func, np.asarray([0.5, 0.5]), method='hybr')['x']

        p1 = bez_func_1(k[0])
        n1 = normalize(rotate_vector(diff_func_1(k[0]), PI / 2))
        p2 = bez_func_2(k[1])
        n2 = normalize(rotate_vector(diff_func_2(k[1]), PI / 2))
        d, center = find_crossing(p1, p2, n1, n2)
        r = abs(d[0])
        start_angle = np.arctan2((p1 - center)[1], (p1 - center)[0])
        cval = np.dot(p1 - center, p2 - center)
        sval = (np.cross(p1 - center, p2 - center))[2]
        angle = np.arctan2(sval, cval)

        out_param = {'radius': r, 'arc_center': center, 'start_angle': start_angle, 'angle': angle}
        return out_param, k

    @staticmethod
    def apply(mob: VMobject, radius: float = 0.2) -> VMobject:
        """Apply rounded corners to a VMobject"""
        i = 0
        while i < mob.get_num_curves() and i < 1e5:
            ind1 = i % mob.get_num_curves()
            ind2 = (i + 1) % mob.get_num_curves()
            curve_1 = mob.get_nth_curve_points(ind1)
            curve_2 = mob.get_nth_curve_points(ind2)
            handle1 = curve_1[-1, :] - curve_1[-2, :]
            handle2 = curve_2[1, :] - curve_2[0, :]
            angle_test = angle_between_vectors_signed(handle1, handle2)
            
            if abs(angle_test) > 1E-6:
                params, k = RoundCorners.round_corner_param(radius, curve_1, curve_2)
                cut_curve_points_1 = partial_bezier_points(curve_1, 0, k[0])
                cut_curve_points_2 = partial_bezier_points(curve_2, k[1], 1)
                loc_arc = Arc(**params, num_components=5)
                mob.points[ind1 * 4:(ind1 + 1) * 4, :] = cut_curve_points_1
                mob.points[ind2 * 4:(ind2 + 1) * 4, :] = cut_curve_points_2
                mob.points = np.insert(mob.points, ind2 * 4, loc_arc.points, axis=0)
                i = i + loc_arc.get_num_curves() + 1
            else:
                i = i + 1

            if i == mob.get_num_curves() - 1 and not mob.is_closed():
                break

        return mob


class ChamferCorners:
    """Utility class for chamfering corners of VMobjects"""
    
    @staticmethod
    def chamfer_corner_param(offset: Union[float, List[float]], curve_points_1: np.ndarray,
                           curve_points_2: np.ndarray) -> Tuple[Dict, List[float]]:
        """Calculate parameters for chamfering a corner"""
        if hasattr(offset, '__iter__'):
            ofs = [offset[0], offset[1]]
        else:
            ofs = [offset, offset]
            
        bez_func_1 = bezier(curve_points_1)
        bez_func_2 = bezier(curve_points_2)

        def get_norms_and_refs(curve):
            sample_points = 10
            refs = np.linspace(0, 1, sample_points)
            points = np.array([curve(a) for a in np.linspace(0, 1, sample_points)])
            diffs = points[1:] - points[:-1]
            norms = np.cumsum(np.apply_along_axis(np.linalg.norm, 1, diffs))
            norms = np.insert(norms, 0, 0)
            return norms, refs

        norms1, refs1 = get_norms_and_refs(bez_func_1)
        norms2, refs2 = get_norms_and_refs(bez_func_2)
        a1 = np.interp(norms1[-1] - ofs[0], norms1, refs1)
        a2 = np.interp(ofs[1], norms2, refs2)
        p1 = bez_func_1(a1)
        p2 = bez_func_2(a2)
        param = {'start': p1, 'end': p2}

        return param, [a1, a2]

    @staticmethod
    def apply(mob: VMobject, offset: float = 0.2) -> VMobject:
        """Apply chamfered corners to a VMobject"""
        i = 0
        while i < mob.get_num_curves() and i < 1e5:
            ind1 = i % mob.get_num_curves()
            ind2 = (i + 1) % mob.get_num_curves()
            curve_1 = mob.get_nth_curve_points(ind1)
            curve_2 = mob.get_nth_curve_points(ind2)
            handle1 = curve_1[-1, :] - curve_1[-2, :]
            handle2 = curve_2[1, :] - curve_2[0, :]
            angle_test = angle_between_vectors_signed(handle1, handle2)
            
            if abs(angle_test) > 1E-6:
                params, k = ChamferCorners.chamfer_corner_param(offset, curve_1, curve_2)
                cut_curve_points_1 = partial_bezier_points(curve_1, 0, k[0])
                cut_curve_points_2 = partial_bezier_points(curve_2, k[1], 1)
                loc_line = Line(**params)
                mob.points[ind1 * 4:(ind1 + 1) * 4, :] = cut_curve_points_1
                mob.points[ind2 * 4:(ind2 + 1) * 4, :] = cut_curve_points_2
                mob.points = np.insert(mob.points, ind2 * 4, loc_line.points, axis=0)
                i = i + loc_line.get_num_curves() + 1
            else:
                i = i + 1

            if i == mob.get_num_curves() - 1 and not mob.is_closed():
                break

        return mob


# ============= Dimensions =============

class CADArrowHead(VMobject):
    """Custom arrowhead for CAD-style dimensions"""
    
    def __init__(self, target_curve: VMobject, anchor_point: float = 1,
                 arrow_size: float = DEFAULT_ARROW_TIP_LENGTH,
                 reversed_arrow: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.target_curve = target_curve
        self.anchor_point = anchor_point
        self._reversed_arrow = reversed_arrow
        
        # Create arrowhead shape
        self.set_points_as_corners([
            LEFT * 2 + UP,
            ORIGIN,
            LEFT * 2 + DOWN
        ])
        
        self.set_arrow_size(arrow_size)
        self.match_style(target_curve)
        self.update_position()
        
    def update_position(self):
        """Update arrowhead position on the curve"""
        point = self.target_curve.point_from_proportion(self.anchor_point)
        
        # Get tangent direction
        if self.anchor_point == 0:
            tangent = self.target_curve.points[1] - self.target_curve.points[0]
        elif self.anchor_point == 1:
            tangent = self.target_curve.points[-1] - self.target_curve.points[-2]
        else:
            # Sample nearby points for tangent
            delta = 0.001
            p1 = self.target_curve.point_from_proportion(max(0, self.anchor_point - delta))
            p2 = self.target_curve.point_from_proportion(min(1, self.anchor_point + delta))
            tangent = p2 - p1
            
        angle = angle_of_vector(tangent)
        if self._reversed_arrow:
            angle += PI
            
        self.rotate(angle)
        self.move_to(point)
        
    def set_arrow_size(self, arrow_size: float):
        """Set the size of the arrowhead"""
        current_size = self.get_width()
        if current_size != 0:
            self.scale(arrow_size / current_size)


class LinearDimension(VDict):
    """Linear dimension with arrows and text"""
    
    def __init__(self, start: np.ndarray, end: np.ndarray,
                 text: Optional[Union[str, VMobject]] = None,
                 direction: np.ndarray = ORIGIN,
                 outside_arrow: bool = False,
                 offset: float = 2,
                 ext_line_offset: float = 0,
                 tip_len: float = DEFAULT_ARROW_TIP_LENGTH,
                 **kwargs):
        super().__init__(**kwargs)
        
        # Set default color if not specified
        if 'color' not in kwargs:
            kwargs['color'] = CADObject.DEFAULT_CAD_COLOR
        if 'stroke_width' not in kwargs:
            kwargs['stroke_width'] = CADObject.DEFAULT_STROKE_WIDTH
            
        self.start = start
        self.end = end
        diff_vect = end - start
        norm_vect = normalize(rotate_vector(diff_vect, PI / 2))

        if np.array_equal(direction, ORIGIN):
            ofs_vect = norm_vect * offset
            ofs_dir = norm_vect
        else:
            ofs_dir = normalize(direction)
            ofs_vect = ofs_dir * offset

        startpoint = start + ofs_dir * np.dot((diff_vect), ofs_dir) / 2 + ofs_vect
        endpoint = end - ofs_dir * np.dot((diff_vect), ofs_dir) / 2 + ofs_vect

        # Create main line
        if not outside_arrow:
            arrow_offset = kwargs.get('stroke_width', DEFAULT_STROKE_WIDTH) * 1 / 100
            ext_dir = normalize(endpoint - startpoint)
            main_line = Line(
                start=startpoint + arrow_offset * ext_dir,
                end=endpoint - arrow_offset * ext_dir,
                **kwargs
            )
            arrow1 = CADArrowHead(main_line, anchor_point=1, arrow_size=tip_len, reversed_arrow=False)
            arrow2 = CADArrowHead(main_line, anchor_point=0, arrow_size=tip_len, reversed_arrow=True)
        else:
            extension = tip_len * 3 * (normalize(endpoint - startpoint))
            main_line = Line(start=startpoint - extension, end=endpoint + extension, **kwargs)
            arrow1 = CADArrowHead(main_line, anchor_point=1, arrow_size=tip_len, reversed_arrow=True)
            arrow2 = CADArrowHead(main_line, anchor_point=0, arrow_size=tip_len, reversed_arrow=False)

        # Extension lines
        self.add({
            'ext_line_1': Line(start=start + ofs_dir * ext_line_offset,
                              end=startpoint + 0.25 * normalize(startpoint - start), **kwargs),
            'ext_line_2': Line(start=end + ofs_dir * ext_line_offset,
                              end=endpoint + 0.25 * normalize(endpoint - end), **kwargs),
            'main_line': main_line,
            'arrow1': arrow1,
            'arrow2': arrow2
        })

        # Add text
        if isinstance(text, str):
            textmob = Text(text, **kwargs)
            textmob.set_stroke(opacity=0)
        elif isinstance(text, VMobject):
            textmob = text
        else:
            dist = np.linalg.norm(startpoint - endpoint)
            textmob = Text(f"{dist:.2f}", **kwargs)
            textmob.set_stroke(opacity=0)

        text_angle = (main_line.get_angle() + PI / 2) % PI - PI / 2
        if abs(text_angle + PI / 2) < 1e-8:
            text_angle = PI / 2
            
        text_h = textmob.height
        text_w = textmob.width
        text_space = np.linalg.norm(self.start - self.end) - tip_len * 2 if not outside_arrow else np.linalg.norm(self.start - self.end)

        if text_w > (text_space * 0.8):
            textmob.scale((text_space * 0.8) / text_w)
            text_h = textmob.height

        textmob.rotate(text_angle)
        textmob.move_to(main_line.get_center() + rotate_vector(UP, text_angle) * text_h)
        self.add({'text': textmob})


class AngularDimension(VDict):
    """Angular dimension with arc and arrows"""
    
    def __init__(self, start: np.ndarray, end: np.ndarray, arc_center: np.ndarray,
                 offset: float = 2,
                 text: Optional[Union[str, VMobject]] = None,
                 outside_arrow: bool = False,
                 ext_line_offset: float = 0,
                 tip_len: float = DEFAULT_ARROW_TIP_LENGTH,
                 **kwargs):
        super().__init__(**kwargs)
        
        # Set default color if not specified
        if 'color' not in kwargs:
            kwargs['color'] = CADObject.DEFAULT_CAD_COLOR
        if 'stroke_width' not in kwargs:
            kwargs['stroke_width'] = CADObject.DEFAULT_STROKE_WIDTH

        self.angle = angle_between_vectors_signed(start - arc_center, end - arc_center)
        radius = (np.linalg.norm(start - arc_center) + np.linalg.norm(end - arc_center)) / 2 + offset
        angle_0 = angle_of_vector(start - arc_center)
        angle_1 = angle_between_vectors_signed(start - arc_center, end - arc_center)

        base_arc = Arc(radius=radius, start_angle=angle_0, arc_center=arc_center,
                      angle=angle_1, **kwargs)
        
        arc_p0 = base_arc.point_from_proportion(0)
        arc_p1 = base_arc.point_from_proportion(1)
        
        # Extension lines
        line1 = Line(start=start + normalize(arc_p0 - start) * ext_line_offset,
                    end=arc_p0 + normalize(arc_p0 - start) * tip_len, **kwargs)
        line2 = Line(start=end + normalize(arc_p1 - end) * ext_line_offset,
                    end=arc_p1 + normalize(arc_p1 - end) * tip_len, **kwargs)
        
        self.add({'ext_line_1': line1, 'ext_line_2': line2})

        if not outside_arrow:
            arrow1 = CADArrowHead(base_arc, anchor_point=1, arrow_size=tip_len, reversed_arrow=False)
            arrow2 = CADArrowHead(base_arc, anchor_point=0, arrow_size=tip_len, reversed_arrow=True)
            self.add({'base_arc': base_arc, 'arrow1': arrow1, 'arrow2': arrow2})
        else:
            extension = tip_len * 3 * np.sign(angle_1)
            angle_ext = extension / radius
            base_arc = Arc(radius=radius, start_angle=angle_0 - angle_ext,
                          angle=self.angle + angle_ext * 2, arc_center=arc_center, **kwargs)
            arrow1 = CADArrowHead(base_arc, anchor_point=1, arrow_size=tip_len, reversed_arrow=True)
            arrow2 = CADArrowHead(base_arc, anchor_point=0, arrow_size=tip_len, reversed_arrow=False)
            self.add({'base_arc': base_arc, 'arrow1': arrow1, 'arrow2': arrow2})

        # Add text
        if isinstance(text, str):
            textmob = Text(text, **kwargs)
            textmob.set_stroke(opacity=0)
        elif isinstance(text, VMobject):
            textmob = text
        else:
            textmob = Text(f"{abs(angle_1 / DEGREES):.0f}°", **kwargs)
            textmob.set_stroke(opacity=0)

        pos_text = base_arc.point_from_proportion(0.5)
        angle_text = (angle_of_vector(base_arc.point_from_proportion(0.5 + 1e-6) -
                                    base_arc.point_from_proportion(0.5 - 1e-6)) + PI / 2) % PI - PI / 2
        if abs(angle_text + PI / 2) < 1e-8:
            angle_text = PI / 2
            
        text_h = textmob.height
        textmob.rotate(angle_text)
        textmob.move_to(pos_text + rotate_vector(UP, angle_text) * text_h)
        self.add({'text': textmob})


class PointerLabel(VDict):
    """Pointer with label for annotations"""
    
    def __init__(self, point: np.ndarray, text: Union[str, VMobject],
                 offset_vector: np.ndarray = RIGHT + DOWN,
                 pointer_offset: float = 0,
                 **kwargs):
        super().__init__(**kwargs)
        
        # Set default color if not specified
        if 'color' not in kwargs:
            kwargs['color'] = CADObject.DEFAULT_CAD_COLOR
        if 'stroke_width' not in kwargs:
            kwargs['stroke_width'] = CADObject.DEFAULT_STROKE_WIDTH
            
        text_buff = 0.1
        
        # Create text
        if isinstance(text, str):
            textmob = Text(text, **kwargs)
        elif isinstance(text, VMobject):
            textmob = text
        else:
            textmob = Text('A', **kwargs)
            
        self.add({'text': textmob})
        
        twidth = textmob.get_width() + text_buff * 2
        stroke_width_loc = kwargs.get('stroke_width', DEFAULT_STROKE_WIDTH)
        self.pointer_offset = pointer_offset + stroke_width_loc / 100

        # Create pointer line
        dim_line = VMobject(**kwargs).set_points_as_corners([
            point + normalize(offset_vector) * self.pointer_offset,
            point + offset_vector,
            point + offset_vector + twidth * np.sign(offset_vector[0]) * RIGHT
        ])
        
        self.add({'line': dim_line})
        
        # Add arrow
        arrow = CADArrowHead(dim_line, anchor_point=0, **kwargs)
        arrow._reversed_arrow = True
        arrow.update_position()
        self.add({'arrow': arrow})
        
        # Position text
        theight = textmob.get_height()
        textmob.move_to(dim_line.points[3, :] + UP * theight * 0.75,
                       aligned_edge=LEFT * np.sign(offset_vector[0]))


# ============= Hatching =============

class HatchPattern(VGroup):
    """Create hatching pattern inside a shape"""
    
    def __init__(self, target_mobject: VMobject, angle: float = PI / 6,
                 spacing: float = 0.3, **kwargs):
        super().__init__(**kwargs)
        self.target = target_mobject
        
        # Calculate bounding box
        target_size_xy = [
            self.target.get_critical_point(RIGHT) - self.target.get_critical_point(LEFT),
            self.target.get_critical_point(UP) - self.target.get_critical_point(DOWN)
        ]
        target_size_diag = np.linalg.norm(target_size_xy)
        num_lines = int(target_size_diag // spacing)
        
        line_v = np.array([np.cos(angle), np.sin(angle), 0])
        offs_v = np.array([-np.sin(angle), np.cos(angle), 0])
        center = self.target.get_center()
        
        for k in range(num_lines * 2):
            line_loc = Line(
                center - line_v * target_size_diag * 1.5,
                center + line_v * target_size_diag * 1.5
            )
            line_loc.shift((k - (num_lines - 1)) * offs_v * spacing)
            
            # Find intersections with target shape
            intersect_idx = self._curve_intersection(self.target, line_loc)
            if any(intersect_idx[1]):
                intersect_indexes = sorted(intersect_idx[1])
                for j in range(len(intersect_idx[1]) // 2):
                    idx1 = int(intersect_indexes[0 + 2 * j] // 1)
                    alpha1 = intersect_indexes[0 + 2 * j] % 1
                    idx2 = int(intersect_indexes[1 + 2 * j] // 1)
                    alpha2 = intersect_indexes[1 + 2 * j] % 1
                    point1 = line_loc.get_nth_curve_function(idx1)(alpha1)
                    point2 = line_loc.get_nth_curve_function(idx2)(alpha2)
                    line_segment = Line(start=point1, end=point2, **kwargs)
                    self.add(line_segment)
                    
    def _curve_intersection(self, vmob1: VMobject, vmob2: VMobject) -> Tuple[np.ndarray, np.ndarray]:
        """Find intersection points between two VMobjects"""
        intersect_indx_1 = np.array([])
        intersect_indx_2 = np.array([])
        
        for i in range(vmob1.get_num_curves()):
            for j in range(vmob2.get_num_curves()):
                curve_1 = vmob1.get_nth_curve_points(i)
                curve_2 = vmob2.get_nth_curve_points(j)
                
                # Check bounding box overlap
                x_range_1 = np.array([np.amax(curve_1[:, 0]), np.amin(curve_1[:, 0])])
                x_range_2 = np.array([np.amax(curve_2[:, 0]), np.amin(curve_2[:, 0])])
                y_range_1 = np.array([np.amax(curve_1[:, 1]), np.amin(curve_1[:, 1])])
                y_range_2 = np.array([np.amax(curve_2[:, 1]), np.amin(curve_2[:, 1])])

                distinct_x = x_range_2[1] > x_range_1[0] or x_range_1[1] > x_range_2[0]
                distinct_y = y_range_2[1] > y_range_1[0] or y_range_1[1] > y_range_2[0]

                overlap = not (distinct_x or distinct_y)

                if overlap:
                    curve_fun_1 = vmob1.get_nth_curve_function(i)
                    curve_fun_2 = vmob2.get_nth_curve_function(j)

                    sol = root(lambda t: (curve_fun_1(t[0])[0:2] - curve_fun_2(t[1])[0:2]), 
                              np.array((0.5, 0.5)))
                    if sol.success:
                        if 0 < sol.x[0] < 1 and 0 < sol.x[1] < 1:
                            intersect_indx_1 = np.append(intersect_indx_1, sol.x[0] + i)
                            intersect_indx_2 = np.append(intersect_indx_2, sol.x[1] + j)

        return intersect_indx_1, intersect_indx_2


# ============= Path utilities =============

class PathMapper:
    """Advanced path analysis and manipulation utilities"""
    
    def __init__(self, path_source: VMobject, num_of_path_points: int = 100):
        self.num_of_path_points = num_of_path_points
        self.path = path_source
        self.generate_length_map()

    def generate_length_map(self):
        """Generate cumulative length mapping for the path"""
        norms = np.array(0)
        for k in range(self.path.get_num_curves()):
            norms = np.append(norms, self.path.get_nth_curve_length_pieces(k, sample_points=11))
        self.pathdata_lengths = np.cumsum(norms)
        self.pathdata_alpha = np.linspace(0, 1, self.pathdata_lengths.size)

    def get_path_length(self) -> float:
        """Get total path length"""
        return self.pathdata_lengths[-1]

    def alpha_from_length(self, s: Union[float, List[float]]) -> Union[float, List[float]]:
        """Convert arc length to alpha parameter"""
        if hasattr(s, '__iter__'):
            return [np.interp(t, self.pathdata_lengths, self.pathdata_alpha) for t in s]
        else:
            return np.interp(s, self.pathdata_lengths, self.pathdata_alpha)

    def length_from_alpha(self, a: Union[float, List[float]]) -> Union[float, List[float]]:
        """Convert alpha parameter to arc length"""
        if hasattr(a, '__iter__'):
            return [np.interp(t, self.pathdata_alpha, self.pathdata_lengths) for t in a]
        else:
            return np.interp(a, self.pathdata_alpha, self.pathdata_lengths)

    def equalize_rate_func(self, rate_func: Callable) -> Callable:
        """Create a rate function that equalizes movement speed along the path"""
        def eq_func(t: float) -> float:
            return self.alpha_from_length(rate_func(t) * self.get_path_length())
        return eq_func

    def point_from_proportion(self, alpha: float) -> np.ndarray:
        """Get point at given proportion along the path with constant speed"""
        a = self.alpha_from_length(alpha * self.get_path_length())
        if a == 1:
            index = self.path.get_num_curves() - 1
            remainder = 1
        else:
            index = int(a * self.path.get_num_curves() // 1)
            remainder = (a * self.path.get_num_curves()) % 1
        return self.path.get_nth_curve_function(index)(remainder)

    def get_tangent_unit_vector(self, s: float) -> np.ndarray:
        """Get unit tangent vector at arc length s"""
        a = self.alpha_from_length(s)
        nc = self.path.get_num_curves()
        indx = int(a * nc // 1)
        bz_a = a * nc % 1
        if indx == nc:
            indx = nc - 1
            bz_a = 1
        points = self.path.get_nth_curve_points(indx)
        dpoints = (points[1:, :] - points[:-1, :]) / 3
        bzf = bezier(dpoints)
        point = bzf(bz_a)
        return normalize(point)

    def get_normal_unit_vector(self, s: float) -> np.ndarray:
        """Get unit normal vector at arc length s"""
        tv = self.get_tangent_unit_vector(s)
        return rotate_vector(tv, PI / 2)


class DashedLine(VDict):
    """Dashed line following a path"""
    
    def __init__(self, target_mobject: VMobject,
                 num_dashes: int = 15,
                 dashed_ratio: float = 0.5,
                 dash_offset: float = 0.0,
                 **kwargs):
        super().__init__(**kwargs)
        self.path = PathMapper(target_mobject, num_of_path_points=10 * target_mobject.get_num_curves())
        
        # Generate dash pattern
        full_len = self.path.get_path_length()
        period = full_len / num_dashes
        dash_len = period * dashed_ratio
        space_len = period * (1 - dashed_ratio)
        n = num_dashes + 2
        
        dash_starts = []
        dash_ends = []
        for i in range(n):
            start = i * period + (dash_offset - 1) * period
            end = start + dash_len
            if 0 <= end and start <= full_len:
                dash_starts.append(max(0, start))
                dash_ends.append(min(full_len, end))
        
        # Create dash mobjects
        a_list = self.path.alpha_from_length(dash_starts)
        b_list = self.path.alpha_from_length(dash_ends)
        dashes = VGroup()
        for i in range(len(dash_starts)):
            mobcopy = VMobject().match_points(target_mobject)
            dashes.add(mobcopy.pointwise_become_partial(target_mobject, a_list[i], b_list[i]))
        
        dashes.match_style(target_mobject)
        self.add({'dashes': dashes})


# Factory functions for easy YAML integration
def create_cad_object(obj_type: str, **params) -> VMobject:
    """Factory function to create CAD objects from YAML configurations"""
    
    # Extract common parameters that shouldn't be passed to constructors
    position = params.pop("position", None)
    
    if obj_type == "rounded_shape":
        shape_type = params.pop("shape", params.pop("shape_type", "square"))
        corner_radius = params.pop("corner_radius", 0.2)
        
        # Extract shape-specific parameters
        color = params.pop("color", WHITE)
        stroke_width = params.pop("stroke_width", 2)
        fill_color = params.pop("fill_color", None)
        fill_opacity = params.pop("fill_opacity", 0)
        
        # Create base shape
        if shape_type == "square":
            side_length = params.pop("side_length", params.pop("size", 2))
            base = Square(side_length=side_length)
        elif shape_type == "rectangle":
            width = params.pop("width", 2)
            height = params.pop("height", 1)
            base = Rectangle(width=width, height=height)
        elif shape_type == "triangle":
            radius = params.pop("radius", params.pop("size", 1))
            base = Triangle(radius=radius)
        elif shape_type == "polygon":
            n = params.pop("n", 6)
            radius = params.pop("radius", params.pop("size", 1))
            base = RegularPolygon(n=n, radius=radius)
        else:
            base = Square()
        
        # Apply styling
        base.set_stroke(color=color, width=stroke_width)
        if fill_color:
            base.set_fill(fill_color, opacity=fill_opacity)
            
        # Apply rounding
        result = RoundCorners.apply(base, corner_radius)
        
        # Apply position if specified
        if position:
            result.move_to(position)
            
        return result
        
    elif obj_type == "chamfered_shape":
        shape_type = params.pop("shape", params.pop("shape_type", "square"))
        chamfer_offset = params.pop("chamfer_offset", 0.2)
        
        # Extract common parameters
        color = params.pop("color", WHITE)
        stroke_width = params.pop("stroke_width", 2)
        fill_color = params.pop("fill_color", None)
        fill_opacity = params.pop("fill_opacity", 0)
        
        # Create base shape
        if shape_type == "square":
            side_length = params.pop("side_length", params.pop("size", 2))
            base = Square(side_length=side_length)
        elif shape_type == "rectangle":
            width = params.pop("width", 2)
            height = params.pop("height", 1)
            base = Rectangle(width=width, height=height)
        elif shape_type == "triangle":
            radius = params.pop("radius", params.pop("size", 1))
            base = Triangle(radius=radius)
        elif shape_type == "polygon":
            n = params.pop("n", 6)
            radius = params.pop("radius", params.pop("size", 1))
            base = RegularPolygon(n=n, radius=radius)
        else:
            base = Square()
        
        # Apply styling
        base.set_stroke(color=color, width=stroke_width)
        if fill_color:
            base.set_fill(fill_color, opacity=fill_opacity)
            
        # Apply chamfering
        result = ChamferCorners.apply(base, chamfer_offset)
        
        # Apply position if specified
        if position:
            result.move_to(position)
            
        return result
        
    elif obj_type == "linear_dimension":
        start = params.pop("start", [-2, 0, 0])
        end = params.pop("end", [2, 0, 0])
        return LinearDimension(np.array(start), np.array(end), **params)
        
    elif obj_type == "angular_dimension":
        start = params.pop("start", [1, 0, 0])
        end = params.pop("end", [0, 1, 0])
        center = params.pop("center", [0, 0, 0])
        return AngularDimension(np.array(start), np.array(end), np.array(center), **params)
        
    elif obj_type == "hatched_shape":
        shape_type = params.pop("shape", params.pop("shape_type", "circle"))
        hatch_angle = params.pop("hatch_angle", PI / 6)
        hatch_spacing = params.pop("hatch_spacing", 0.3)
        
        # Extract common parameters
        color = params.pop("color", WHITE)
        stroke_width = params.pop("stroke_width", 2)
        fill_color = params.pop("fill_color", None)
        fill_opacity = params.pop("fill_opacity", 0)
        
        # Create base shape
        if shape_type == "circle":
            radius = params.pop("radius", params.pop("size", 1))
            base = Circle(radius=radius)
        elif shape_type == "square":
            side_length = params.pop("side_length", params.pop("size", 2))
            base = Square(side_length=side_length)
        elif shape_type == "rectangle":
            width = params.pop("width", 2)
            height = params.pop("height", 1)
            base = Rectangle(width=width, height=height)
        elif shape_type == "triangle":
            radius = params.pop("radius", params.pop("size", 1))
            base = Triangle(radius=radius)
        else:
            base = Circle()
        
        # Apply styling
        base.set_stroke(color=color, width=stroke_width)
        if fill_color:
            base.set_fill(fill_color, opacity=fill_opacity)
            
        # Create hatching
        hatching = HatchPattern(base, angle=hatch_angle, spacing=hatch_spacing)
        hatching.set_stroke(color=color, width=stroke_width * 0.5)  # Thinner lines for hatching
        
        result = VGroup(base, hatching)
        
        # Apply position if specified
        if position:
            result.move_to(position)
            
        return result
        
    elif obj_type == "dashed_shape":
        shape_type = params.pop("shape", "circle")
        num_dashes = params.pop("num_dashes", 15)
        dashed_ratio = params.pop("dashed_ratio", 0.5)
        
        # Extract common parameters
        color = params.pop("color", WHITE)
        stroke_width = params.pop("stroke_width", 2)
        
        # Create base shape
        if shape_type == "circle":
            radius = params.pop("radius", 1.0)
            base = Circle(radius=radius)
        elif shape_type == "square":
            side_length = params.pop("side_length", params.pop("size", 2))
            base = Square(side_length=side_length)
        elif shape_type == "rectangle":
            width = params.pop("width", 2)
            height = params.pop("height", 1)
            base = Rectangle(width=width, height=height)
        elif shape_type == "triangle":
            radius = params.pop("radius", params.pop("size", 1))
            base = Triangle(radius=radius)
        else:
            base = Circle()
        
        # Apply styling
        base.set_stroke(color=color, width=stroke_width)
        
        result = DashedLine(base, num_dashes=num_dashes, dashed_ratio=dashed_ratio)
        
        # Apply position if specified
        if position:
            result.move_to(position)
            
        return result
        
    else:
        # Default to circle
        return Circle(**params)


# Note: CAD objects are available through the create_cad_object factory function
# They can be registered with your scene builder or YAML parser as needed