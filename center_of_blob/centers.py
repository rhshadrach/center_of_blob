class Centers(dict):
    def closest(self, point, radius=None):
        x, y = point
        closest, shortest_distance = None, None
        for x2, y2 in self:
            distance = (x - x2) * (x - x2) + (y - y2) * (y - y2)
            if closest is None or distance < shortest_distance:
                closest = x2, y2
                shortest_distance = distance

        if shortest_distance is None or radius is not None and shortest_distance > radius*radius:
            return None
        return closest
