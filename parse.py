#!/usr/bin/env python3
import struct

def unpack(data, fmt):
    a = struct.unpack(fmt, data)
    if len(a) == 1:
        return a[0]
    else:
        return a

def unpack_file(f, fmt):
    return unpack(f.read(struct.calcsize(fmt)), fmt)

def extract_str(data, off):
    s = b''
    i = 0
    while True:
        if data[off+i] != 0:
            s += data[off+i:off+i+1]
        else:
            break
        i += 1
    return s

class Layout:
    def __init__(self):
        pass

class Pane:
    def __init__(self, name, visibility, origin, alpha, x, y, z, x_rotate, y_rotate, z_rotate, x_scale, y_scale, width, height):
        self.children = []

        self.name = name
        self.visibility = visibility
        self.origin = origin
        self.alpha = alpha
        self.x = x
        self.y = y
        self.z = z
        self.x_rotate = x_rotate
        self.y_rotate = y_rotate
        self.z_rotate = z_rotate
        self.x_scale = x_scale
        self.y_scale = y_scale
        self.width = width
        self.height = height

    def __str__(self):
        children = ",".join(map(str, self.children))
        return "Pane<name={},children=[{}]".format(self.name,children)

    def __repr__(self):
        children = ",".join(map(repr, self.children))
        return "Pane<name={}, visibility={}, origin={}, alpha={}, x,y,z=[{},{},{}], rotate=[{},{},{}], scale=[{},{}], size=[{},{}], children=[{}]>".format(self.name,self.visibility,self.origin,self.alpha,self.x,self.y,self.z,self.x_rotate,self.y_rotate,self.z_rotate,self.x_scale,self.y_scale,self.width,self.height,children)

class ImagePane:
    def __init__(self, name, visibility, origin, alpha, alpha2, x, y, z, x_flip, y_flip, angle, x_mag, y_mag, width, height, unk_blob):
        self.children = []
        self.name = name
        self.visibility = visibility
        self.origin = origin
        self.alpha = alpha
        self.alpha2 = alpha2
        self.x = x
        self.y = y
        self.z = z
        self.x_flip = x_flip
        self.y_flip = y_flip
        self.angle = angle
        self.x_mag = x_mag
        self.y_mag = y_mag
        self.width = width
        self.height = height

        self.unk_blob = unk_blob

    def __str__(self):
        children = ",".join(map(str, self.children))
        s = "ImagePane<name={}"
        if len(self.children) != 0:
            s += ",children=[{}]"
        s += ">"
        return s.format(self.name, children)

    def __repr__(self):
        children = ",".join(map(repr, self.children))
        s = "ImagePane<name={}, visibility={}, origin={}, alpha={}, x,y,z=[{},{},{}], flip=[{},{}], mag=[{},{}], size=[{},{}],"
        if len(self.children) != 0:
            s += ",children=[{}]"
        s += ">"
        return s.format(self.name,self.visibility,self.origin,self.alpha,self.x,self.y,self.z,self.x_flip,self.y_flip,self.x_mag,self.y_mag,self.width,self.height,children)

class Material:
    def __init__(self, name, colors, flags, texture_index, mapping, x, y, rotation, x_scale, y_scale):
        self.name = name
        self.colors = colors
        self.flags = flags
        self.texture_index = texture_index
        self.mapping = mapping
        self.x = x
        self.y = y
        self.rotation = rotation
        self.x_scale = x_scale
        self.y_scale = y_scale

class Group():
    def __init__(self, name, elements):
        self.name = name
        self.children = []
        self.elements = elements
    
    def __str__(self):
        children = ",".join(map(str, self.children))
        s = "ImagePane<name={}"
        if len(self.children) != 0:
            s += ",children=[{}]"
        s += ">"
        return s.format(self.name, children)

    def __repr__(self):
        children = ",".join(map(repr, self.children))
        s = "Group<name={}, elements=[{}]"
        if len(self.children) != 0:
            s += ",children=[{}]"
        s += ">"
        return s.format(self.name, self.elements, children)

class LayoutFile:
    @staticmethod
    def from_file(f):
        lyt = LayoutFile()
        lyt.f = f
        if f.read(4) != b'CLYT':
            raise Exception("Bad CLYT header")

        bom = unpack_file(f, "H")
        if bom != 0xfeff:
            raise Exception("Bad BOM (should be ef ff for a LE BCLYT)")

        header_length = unpack_file(f, "H")
        header = f.read(header_length - 8)
        lyt.revision = unpack(header[0:4], "I")
        lyt.filesize = unpack(header[4:8], "I")
        lyt.num_sections = unpack(header[8:12], "I")

        lyt.materials = {}
        lyt.textures = []
        lyt.root_pane = None
        lyt.root_group = None

        lyt.last_pane = None
        lyt.last_group = None
        lyt.current_panes = []
        lyt.current_groups = []

        for i in range(0, lyt.num_sections):
            res = lyt.read_section()

        print(repr(lyt.root_pane))
        print(repr(lyt.root_group))

        return lyt

    def gen_sections(self):
        self.sections = []

        self.add_layout_section()
        self.add_textures_section()
        self.add_materials_section()
        self.emit_pane(self.root_pane)
        self.emit_group(self.root_group)

    def add_section(self, magic, data):
        self.sections.append((magic, data))

    def add_layout_section(self):
        self.add_section(b'lyt1', struct.pack('bxxxff', self.centered, self.width, self.height))

    def add_textures_section(self):
        data = b''
        offs = []
        for t in self.textures:
            offs.append(len(data) + 8)
            data += t + b'\x00'

        section_data = struct.pack('HH' + str(len(offs))+'I', len(self.textures), 0, *offs) + data

        if len(section_data) % 4 != 0:
            section_data += b'\x00' * (len(section_data) % 4)

        self.add_section(b'txl1', section_data)

    def add_materials_section(self):
        data = b''
        offs = []
        len_offs = len(self.materials) * 4
        for m in self.materials:
            m = self.materials[m]
            offs.append(len(data) + 12 + len_offs)
            data += struct.pack('20s', m.name)
            data += struct.pack('7I', *m.colors)
            data += struct.pack('I', m.flags)
            data += struct.pack('I', m.texture_index | m.mapping)
            data += struct.pack('5f', m.x, m.y, m.rotation, m.x_scale, m.y_scale)
            data += struct.pack('I', 0)


        section_data = struct.pack('HH' + str(len(offs))+'I', len(self.textures), 0, *offs) + data
        self.add_section(b'mat1', section_data)

    def emit_pane(self, pane):
        print(pane)
        if isinstance(pane, Pane):
            self.emit_null_pane(pane)
        elif isinstance(pane, ImagePane):
            self.emit_img_pane(pane)

    def emit_null_pane(self, pane):
        section_data = b''
        section_data += struct.pack('BBBB', pane.visibility, pane.origin, pane.alpha, 0)
        section_data += struct.pack('20s', pane.name)
        section_data += struct.pack('I', 0)
        section_data += struct.pack('3f', pane.x, pane.y, pane.z)
        section_data += struct.pack('3f', pane.x_rotate, pane.y_rotate, pane.z_rotate)
        section_data += struct.pack('2f', pane.x_scale, pane.y_scale)
        section_data += struct.pack('2f', pane.width, pane.height)
        self.add_section(b'pan1', section_data)

        if len(pane.children) != 0:
            self.add_section(b'pas1', b'')
            for child in pane.children:
                self.emit_pane(child)
            self.add_section(b'pae1', b'')

    def emit_img_pane(self, pane):
        section_data = b''
        section_data += struct.pack('BBBB', pane.visibility, pane.origin, pane.alpha, pane.alpha2)
        section_data += struct.pack('20s', pane.name)
        section_data += struct.pack('I', 0)
        section_data += struct.pack('3f', pane.x, pane.y, pane.z)
        section_data += struct.pack('2f', pane.x_flip, pane.y_flip)
        section_data += struct.pack('f', pane.angle)
        section_data += struct.pack('2f', pane.x_mag, pane.y_mag)
        section_data += struct.pack('2f', pane.width, pane.height)
        
        section_data += pane.unk_blob

        self.add_section(b'pic1', section_data)

    def emit_group(self, group):
        section_data = b''
        section_data += struct.pack('16s', group.name)
        section_data += struct.pack('HH', len(group.elements), 0)
        for i in range(0, len(group.elements)):
            section_data += struct.pack('16s', group.elements[i])

        self.add_section(b'grp1', section_data)

        if len(group.children) != 0:
            self.add_section(b'grs1', b'')
            for child in group.children:
                self.emit_group(child)
            self.add_section(b'gre1', b'')

    def save(self, f):
        self.gen_sections()

        f.write(b'CLYT')
        f.write(struct.pack('H', 0xfeff))
        header_length = 12

        self.filesize = header_length + 8 + sum(map(lambda a: len(a[1]) + 8, self.sections))

        print(self.filesize)

        header = struct.pack('III', self.revision, self.filesize, len(self.sections))
        f.write(struct.pack('H', header_length + 8))
        f.write(header)

        for s in self.sections:
            f.write(s[0])
            f.write(struct.pack('I', len(s[1]) + 8))
            f.write(s[1])

    def read_section(self):
        magic = self.f.read(4)
        size = unpack_file(self.f, "I")

        def group_start(data):
            self.current_groups.append(self.last_group)
        
        def group_end(data):
            self.current_groups.pop()

        def group(data):
            name = data[0:0x10].strip(b'\x00')
            num_entries = unpack(data[0x10:0x12], 'H')
            elements = []

            for i in range(0, num_entries):
                sub_name = data[0x14 + i * 0x10:0x24 + i * 0x10].strip(b'\x00')
                elements.append(sub_name)
            
            g = Group(name = name, elements = elements)
            self.last_group = g

            if len(self.current_groups) != 0:
                self.current_groups[-1].children.append(g)
            else:
                self.root_group = g

            return g

        def pane_start(data):
            self.current_panes.append(self.last_pane)

        def pane_end(data):
            self.current_panes.pop()

        def pane(data):
            visibility = data[0]
            origin = data[1]
            alpha = data[2]

            name = data[0x4:0x14].strip(b'\x00')
            x, y, z, x_rotate, y_rotate, z_rotate, x_scale, y_scale, width, height = unpack(data[0x1c:0x44], "10f")

            #print("Null pane, name={}, visibility={}, origin={}, x,y,z=[{},{},{}], rotate=[{},{},{}], scale=[{},{}], size=[{},{}]".format(name,visibility,origin,x,y,z,x_rotate,y_rotate,z_rotate,x_scale,y_scale,width,height))

            p = Pane(name=name, visibility=visibility, origin=origin, alpha=alpha, x=x, y=y, z=z, x_rotate=x_rotate, y_rotate=y_rotate, z_rotate=z_rotate, x_scale=x_scale, y_scale=y_scale, width=width, height=height)
            if len(self.current_panes) != 0:
                self.current_panes[-1].children.append(p)
            else:
                self.root_pane = p

            self.last_pane = p
            return p

        def img_pane(data):
            #print(hex(self.f.tell() - len(data)))
            visibility = data[0]
            origin = data[1]
            alpha = data[2]
            alpha2 = data[3]
            name = data[0x4:0x14].strip(b'\x00')
            x, y, z, x_flip, y_flip, angle, x_mag, y_mag, width, height = unpack(data[0x1c:0x44], "10f")
            unk = data[0x44:0x78]

            #print("Image pane, name={}, visibility={}, origin={}, x,y,z=[{},{},{}], flip=[{},{}], mag=[{},{}], size=[{},{}]".format(name,visibility,origin,x,y,z,x_flip,y_flip,x_mag,y_mag,width,height))

            p = ImagePane(name=name, visibility=visibility, origin=origin, alpha=alpha, alpha2=alpha2 , x=x, y=y, z=z, x_flip=x_flip, y_flip=y_flip, angle=angle, x_mag=x_mag, y_mag=y_mag, width=width, height=height, unk_blob=unk)
            p.children = []
            if len(self.current_panes) != 0:
                self.current_panes[-1].children.append(p)

            return p

        handlers = {
            b'lyt1': self.parse_layout,
            b'txl1': self.parse_txl,
            b'mat1': self.parse_materials,
            b'pan1': pane,
            b'pas1': pane_start,
            b'pae1': pane_end,
            b'pic1': img_pane,
            b'grp1': group,
            b'grs1': group_start,
            b'gre1': group_end
        }

        if not magic in handlers:
            raise Exception("Unknown section {}".format(magic))
        else:
            return handlers[magic](self.f.read(size-8))

    def parse_layout(self, data):
        centered = data[0] != 0
        w,h = unpack(data[4:12], "2f")
        #print("Layout:")
        #print("centered={} width={}, height={}".format(centered, w, h))
        self.centered = centered
        self.width = w
        self.height = h

    def parse_txl(self, data):
        num_filenames = unpack(data[0:2], "H")
        print("There are {} textures".format(num_filenames))
        offsets = struct.unpack("I" * num_filenames, data[4:4+num_filenames*4])
        i = 0
        for o in offsets:
            o += 4
            self.textures.append(extract_str(data, o))
            print(hex(o), extract_str(data, o))

    def parse_materials(self, data):
        num_materials = unpack(data[0:2], "H")
        print("There are {} materials.".format(num_materials))
        offsets = struct.unpack("I" * num_materials, data[4:4+num_materials*4])

        for o in offsets:
            o -= 8 # Offset of section magic + size that were removed.
            mat_name = data[o:o+0x14].strip(b'\x00')
            print("Material name: {}".format(mat_name))
            
            colors = unpack(data[o+0x14:o+0x14+7*4], "7I")
            print("colors:", list(map(lambda a:"{:08x}".format(a),colors)))

            flags = unpack(data[o+0x30:o+0x34], "I")
            tex_idx_and_mapping = unpack(data[o+0x34:o+0x38], "I")
            print("flags: {:x}, tex_idx_and_mapping: {:x}".format(flags, tex_idx_and_mapping))
            x,y,rotation,x_scale,y_scale = unpack(data[o+0x38:o+0x4c], "5f")
            unk = unpack(data[o+0x4c:o+0x50], "I")
            print("pos=[{}, {}], scale=[{}, {}], rotation={}".format(x,y,x_scale,y_scale,rotation))

            self.materials[mat_name] = Material(name = mat_name, colors=colors, flags=flags, texture_index=tex_idx_and_mapping, mapping=tex_idx_and_mapping, x=x,y=y,rotation=rotation,x_scale=x_scale,y_scale=y_scale)