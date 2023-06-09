import bpy
import math
import os


# Set render engine and adjust render parameters
def config_render(engine='cycles', device='GPU', samples=32, use_denoising=False, resolution_x=1920, resolution_y=1080,
                  focal_length=20):
    # Set image resolution and focal length
    bpy.context.scene.render.resolution_x = resolution_x
    bpy.context.scene.render.resolution_y = resolution_y
    # bpy.context.object.data.lens = focal_length

    # Adjust cycles render engine parameters
    if engine == 'cycles':
        bpy.context.scene.render.engine = 'CYCLES'
        scene = bpy.context.scene.cycles
        scene.feature_set = 'EXPERIMENTAL'
        scene.device = device
        scene.samples = samples  # Number of samples to render for each pixel
        scene.use_denoising = use_denoising
        scene.dicing_rate = 2  # Size of micropolygon in pixels
        scene.offscreen_dicing_scale = 10  # Multiplier for dicing rate of geometry outside of the camera view
        scene.max_subdivisions = 12

    # Adjust eevee render engine parameters
    elif engine == 'eevee':
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'
        scene = bpy.context.scene.eevee
        bpy.context.scene.eevee.taa_render_samples = samples  # Number of samples to render for each pixel

    else:
        print('please write a valid render engine')


# Unlink native sky, link HDRI to background node and set its strength
def config_sky(name, hdri_list=["CAVOK twilight", "Coast", "OVC", "SCT"], fog_list=['Intense fog', 'Dust'], path='//HDRI/'):
    
    sky_texture = bpy.data.worlds["World"].node_tree.nodes["Sky Texture"]
    # Get the environment node tree of the current scene
    env_texture = bpy.data.worlds["World"].node_tree.nodes['Environment Texture']

    if name in hdri_list:

        # Load HDRI and adjust its strength
        hdri_dir = path + name + '.hdr'
        env_texture.image = bpy.data.images.load(hdri_dir)

        # Link HDRI node to background node and adjust strength
        links = bpy.context.scene.world.node_tree.links
        links.new(env_texture.outputs[0], bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0])
        bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[1].default_value = 0.4

        # Adjust a specific HDRI
        if name == 'Coast':
            bpy.data.worlds["World"].node_tree.nodes["Mapping"].inputs[1].default_value[2] = 0.04
        elif name == 'CAVOK twilight':
            bpy.data.worlds["World"].node_tree.nodes["Mapping"].inputs[1].default_value[2] = 0.01
        else:
            bpy.data.worlds["World"].node_tree.nodes["Mapping"].inputs[1].default_value[2] = 0

    elif name in fog_list:
        sky_texture.sky_type = 'NISHITA'
        sky_texture.sun_intensity = 0.7
        sky_texture.sun_elevation = 0.785398
        sky_texture.altitude = 0
        sky_texture.air_density = 1
        sky_texture.ozone_density = 0.5
        if name=="Intense fog":
            config_fog(0.9)
            sky_texture.dust_density = 0
            sky_texture.sun_disc = False

        else:
            config_fog(0.8, dust=True)
            sky_texture.dust_density = 1.5
            sky_texture.sun_disc = True

            # Link sky texture node to background node and adjust strength
            links = bpy.context.scene.world.node_tree.links
            links.new(sky_texture.outputs[0], bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0])
            bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[1].default_value = 0.4

    else:
        # Adjust sky texture parameters
        if name == 'CAVOK night':
            sky_texture.sky_type = 'HOSEK_WILKIE'
            sky_texture.turbidity = 2
            sky_texture.ground_albedo = 0.5
        elif name == 'CAVOK mid day':
            sky_texture.sky_type = 'NISHITA'
            sky_texture.sun_disc = True
            sky_texture.sun_intensity = 0.7
            sky_texture.sun_elevation = 0.785398
            sky_texture.altitude = 0
            sky_texture.air_density = 1
            sky_texture.dust_density = 0
            sky_texture.ozone_density = 0.5
        else:
            print('please write a valid sky texture')

        # Link sky texture node to background node and adjust strength
        links = bpy.context.scene.world.node_tree.links
        links.new(sky_texture.outputs[0], bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0])
        bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[1].default_value = 0.4


# Adjust fog parameters
def config_fog(intensity, clamp=True, start_distance=50, max_distance=50000, evolution_type='quadratic', dust=False):
    bpy.data.scenes["Scene"].node_tree.nodes["Mix"].inputs[0].default_value = intensity
    bpy.data.scenes["Scene"].node_tree.nodes["Mix"].use_clamp = clamp
    bpy.context.scene.world.mist_settings.start = start_distance
    bpy.context.scene.world.mist_settings.depth = max_distance
    bpy.context.scene.world.mist_settings.falloff = evolution_type.upper()

    # Adjust fog color according the existence of dust or not
    if dust == True:
        bpy.data.scenes["Scene"].node_tree.nodes["ColorRamp"].color_ramp.elements[1].color = (0.67609, 0.371454, 0.0267095, 1)
    else:
        bpy.data.scenes["Scene"].node_tree.nodes["ColorRamp"].color_ramp.elements[1].color = (1, 1, 1, 1)


# Enable a certain object in renders and hide all the others
def show_object(name, collection=False):
    
    enabled_objects = ['Camera', 'Ocean', 'TexturePlacement']

    # Hide all non enabled objects
    for object in bpy.context.scene.objects:
        if (object.name in enabled_objects):
            bpy.data.objects[object.name].hide_render = False
        else:
            bpy.data.objects[object.name].hide_render = True

    # Enable the choosen object
    if collection == True:
        bpy.data.collections[name].hide_render = False
        for obj in bpy.data.collections[name].objects:
            bpy.data.objects[obj.name].hide_render = False
    else:
        bpy.data.objects[name].hide_render = False


# Edit one ocean texture, bake a new sequence and import those frames to the ocean
def config_ocean(ocean_number, total_frames, type, resolution=20, random_seed=0, wave_scale=2,
                 wave_scale_min=0, choppiness=1.5, wind_velocity=7, wave_alignment=0.75, wave_direction=0, damping=0.5,
                 use_foam=False, foam_coverage=0.2):
    which_ocean = 'OceanPreview' + str(ocean_number)
    ocean = bpy.data.objects[which_ocean].modifiers["Ocean"]

    # Adjust ocean type
    if type == 'turbulent':
        ocean.spectrum = 'PHILLIPS'
    elif type == 'established':
        ocean.spectrum = 'PIERSON_MOSKOWITZ'
    elif type == 'established_with_peaks':
        ocean.spectrum = 'JONSWAP'
    elif type == 'shallow':
        ocean.spectrum = 'TEXEL_MARSEN_ARSLOE'
    else:
        print('please write a valid ocean type')

    # Adjust the properties of one ocean texture
    ocean.resolution = resolution
    ocean.random_seed = random_seed  # Seed of the random generator
    ocean.wave_scale = wave_scale  # Scale of the displacement effect
    ocean.wave_scale_min = wave_scale_min  # Shortest allowed wavelength
    ocean.choppiness = choppiness  # Scale of the wave's crest
    ocean.wind_velocity = wind_velocity  # Wind speed in m/s
    ocean.wave_alignment = wave_alignment  # How much the waves are aligned to each other
    ocean.wave_direction = wave_direction  # Main direction of the waves when they are (partially) aligned, in rads
    ocean.damping = damping  # Damp reflected waves going on opposite direction to the wind
    ocean.use_foam = use_foam  # Generate foam mask as a vertex color channel
    if ocean.use_foam == True:
        ocean.foam_layer_name = "foam"
        ocean.foam_coverage = foam_coverage  # Amount of generated foam

    # Deselect any selected object
    for obj in bpy.data.objects:
        if obj.select_get() == True:
            obj.select_set(False)

    # Bake an image sequence according to the ocean texture defined
    bpy.data.objects[which_ocean].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[which_ocean]
    bpy.ops.object.ocean_bake(modifier="Ocean")

    # Load those sequences previously baked
    sequence_dir = "//OceanD" + str(ocean_number) + "_test/disp_0001.exr"
    bpy.data.materials["Ocean"].node_tree.nodes["Image Texture"].image = bpy.data.images.load(sequence_dir,
                                                                                              check_existing=True)
    bpy.data.images["disp_0001.exr"].source = 'SEQUENCE'
    bpy.data.materials["Ocean"].node_tree.nodes["Image Texture"].image_user.frame_start = 1
    bpy.data.materials["Ocean"].node_tree.nodes["Image Texture"].image_user.frame_duration = total_frames


# Choose one of the four ocean types available
def choose_ocean(type):
    # Deselect any selected object
    for obj in bpy.data.objects:
        if obj.select_get() == True:
            obj.select_set(False)

    # Load sequences previously baked
    node_texture1 = bpy.data.materials["Ocean"].node_tree.nodes["Image Texture"]
    node_texture2 = bpy.data.materials["Ocean"].node_tree.nodes["Image Texture.001"]
    sequence_dir1 = "//Bakes/" + type + "/texture.01/disp_0001.exr"
    sequence_dir2 = "//Bakes/" + type + "/texture.02/disp_0001.exr"
    node_texture1.image = bpy.data.images.load(sequence_dir1, check_existing=True)
    node_texture2.image = bpy.data.images.load(sequence_dir2, check_existing=True)
    bpy.data.images["disp_0001.exr"].source = 'SEQUENCE'
    node_texture1.image_user.frame_start = 1
    node_texture1.image_user.frame_duration = 250
    node_texture2.image_user.frame_start = 1
    node_texture2.image_user.frame_duration = 250

    metallic_shine = bpy.data.materials["Ocean"].node_tree.nodes["Principled BSDF"].inputs[6].default_value
    noise_scale = bpy.data.materials["Ocean"].node_tree.nodes["Noise Texture.001"].inputs[2].default_value
    node1_color0 = bpy.data.materials["Ocean"].node_tree.nodes["ColorRamp.001"].color_ramp.elements[0]
    node1_color1 = bpy.data.materials["Ocean"].node_tree.nodes["ColorRamp.001"].color_ramp.elements[1]
    node2_color0 = bpy.data.materials["Ocean"].node_tree.nodes["ColorRamp"].color_ramp.elements[0]
    node2_color1 = bpy.data.materials["Ocean"].node_tree.nodes["ColorRamp"].color_ramp.elements[1]

    # Specific adjustments to each ocean
    if type == 'Shallow':
        metallic_shine = 0.25
        node1_color0.position = 0.164
        node1_color0.color = (0, 0, 0, 1)
        node1_color1.position = 0.741
        node1_color1.color = (1, 1, 1, 1)
        node2_color0.position = 0
        node2_color0.color = (0, 0, 0, 1)
        node2_color1.position = 1
        node2_color1.color = (0.522, 0.522, 0.522, 1)
        create_foam(foam=False)
    elif type == 'Established':
        metallic_shine = 0.25
        node1_color0.position = 0
        node1_color0.color = (0, 0, 0, 1)
        node1_color1.position = 0.577
        node1_color1.color = (1, 1, 1, 1)
        node2_color0.position = 0.4
        node2_color0.color = (0.162089, 0.162089, 0.162089, 1)
        node2_color1.position = 0.568
        node2_color1.color = (1, 1, 1, 1)
        create_foam(foam=False)
    elif type == 'Established with peaks':
        metallic_shine = 0.75
        node1_color0.position = 0
        node1_color0.color = (0, 0, 0, 1)
        node1_color1.position = 1
        node1_color1.color = (1, 1, 1, 1)
        node2_color0.position = 0
        node2_color0.color = (0, 0, 0, 1)
        node2_color1.position = 1
        node2_color1.color = (1, 1, 1, 1)
        create_foam(foam=True)
    elif type == 'Turbulent':
        metallic_shine = 0.75
        node1_color0.position = 0
        node1_color0.color = (0.609038, 0.609038, 0.609038, 1)
        node1_color1.position = 1
        node1_color1.color = (1, 1, 1, 1)
        node2_color0.position = 0
        node2_color0.color = (0.687521, 0.687521, 0.687521, 1)
        node2_color1.position = 1
        node2_color1.color = (1, 1, 1, 1)
        create_foam(foam=True)
    else:
        print('please write a valid ocean type')


def create_foam(foam=False):
    principled_bsdf = bpy.data.materials["Ocean"].node_tree.nodes["Principled BSDF"]
    foam_mixer = bpy.data.materials["Ocean"].node_tree.nodes["Mix Shader"]
    material_output = bpy.data.materials["Ocean"].node_tree.nodes["Material Output"]

    if foam == True:
        # Link foam mixer node to material output node
        links = bpy.data.materials["Ocean"].node_tree.links
        links.new(foam_mixer.outputs[0], material_output.inputs[0])

    else:
        # Link sea texture node to material output node
        links = bpy.data.materials["Ocean"].node_tree.links
        links.new(principled_bsdf.outputs[0], material_output.inputs[0])


# Set ocean color
def config_ocean_color(color):
    color_code = bpy.data.materials["Ocean"].node_tree.nodes["Principled BSDF"].inputs[0]
    if color == 'Reflections only':
        color_code.default_value = (0, 0, 0, 1)
    elif color == 'Delft Blue':
        color_code.default_value = (0.00165781, 0.0084868, 0.0425674, 1)
    elif color == 'Aquamarine':
        color_code.default_value = (0.00296434, 0.0235834, 0.0235834, 1)
    else:
        print('please write a valid color name')


# Establish a camera position and rotation for a given frame
def insert_keyframe(keyframe, key_location, key_rotation):
    # Define camera settings
    camera = bpy.context.scene.objects['Camera']
    camera.location = key_location
    camera.rotation_euler = key_rotation  # Rotation in rads

    # Insert keyframe
    camera.keyframe_insert(data_path="location", frame=keyframe)
    camera.keyframe_insert(data_path="rotation_euler", frame=keyframe)


# Delete keyframes
def delete_keyframe(frame_list='all'):
    camera = bpy.context.scene.objects['Camera']

    # Delete all keyframes or just the selected ones
    if frame_list == 'all':
        for frame_number in range(0, 251):  # todo alterar
            camera.keyframe_delete(data_path='location', frame=frame_number)
            camera.keyframe_delete(data_path='rotation_euler', frame=frame_number)
    else:
        for frame_number in frame_list:
            camera.keyframe_delete(data_path='location', frame=frame_number)
            camera.keyframe_delete(data_path='rotation_euler', frame=frame_number)


def set_orbit(dist, height, total_frames=250):

    # Make the conversion from a word to a number
    if dist=='Close':
        camera_dist=500
    elif dist=='Medium':
        camera_dist=2000
    elif dist=='Far':
        camera_dist=4000
    else:
        print('Please insert a valid metric')

    if height=='Low':
        camera_height=200
    elif height=='Medium':
        camera_height=600
    elif height=='High':
        camera_height=1000
    else:
        print('Please insert a valid metric')

    # Estimate camera position and rotation on frame 1
    camera_positions = [(camera_dist, 0, camera_height)]
    camera_rotations = [(math.atan(camera_dist / camera_height), 0, math.pi / 2)]

    # Delete all keyframes and insert first keyframe
    delete_keyframe()
    insert_keyframe(1, camera_positions[0], camera_rotations[0])

    total_keyframes = 5
    step = total_frames / (total_keyframes - 1)
    angle_step = (2 * math.pi) / (total_keyframes - 1)

    # Estimate other positions and rotations
    for i in range(1, total_keyframes):
        last_position = camera_positions[-1]
        last_rotation = camera_rotations[-1]
        next_position = (
        camera_dist * math.cos(i * angle_step), camera_dist * math.sin(i * angle_step), last_position[2])
        next_rotation = (last_rotation[0], last_rotation[1], last_rotation[2] + angle_step)
        camera_positions.append(next_position)
        camera_rotations.append(next_rotation)

        # Insert keyframes
        insert_keyframe(i * step, next_position, next_rotation)


# Render the defined sequence
def render(images_dir, segmentations_dir, sequence=True, frame_start=1, frame_end=250, frame_step=1):
    # Set frames parameters
    bpy.context.scene.frame_start = frame_start
    bpy.context.scene.frame_end = frame_end
    bpy.context.scene.frame_step = frame_step  # Number of frames to skip forward while rendering

    # Set output directory
    bpy.data.scenes["Scene"].node_tree.nodes["File Output"].base_path = images_dir
    bpy.data.scenes["Scene"].node_tree.nodes["File Output.001"].base_path = segmentations_dir

    # Render the images while display the process on a new window
    bpy.ops.render.render(animation=sequence, write_still=True)


output_dir = '/mnt/hdd_2tb_1/fsmatilde/Dataset_Blender/Final+sequence_divided+impossible_sequences/'

# Set render configuration
config_render(engine='cycles', device='GPU', samples=1, resolution_x=1280, resolution_y=720, focal_length=20)

# Open .txt file with all scene combinations
txt_file = open('/mnt/hdd_2tb_1/fsmatilde/Scripts/Scene_combinations.txt', 'r')

counter = 1

# Read file lines and split them into a list
for line in txt_file.readlines():

    if counter not in range(9505, 10369) and counter not in range (11233, 12097):     # impossible sequences

        config = line[:-1].split('-')
        print([counter] + config)

        # Change the scene according to each configuration
        if config[1] == 'None':
            config_fog(0)
        elif config[1] == 'Light':
            config_fog(0.55, clamp=False)
        else:
            print('Please insert a valid fog configuration')
        config_sky(config[0])
        set_orbit(config[2], config[3])
        choose_ocean(config[4])
        config_ocean_color(config[5])
        if config[6] in ['CruiseShip', 'Yacht']:
            show_object(config[6], collection=True)
        else:
            show_object(config[6])

        # Render the sequence and save on a certain directory
        sequence_name = 'Sequence.' + format(counter, "04")
        sequence_dir = output_dir + sequence_name
        render(sequence_dir + '/Images2/', sequence_dir + '/Segmentations_boat_only/', sequence=True, frame_step=20)

    counter += 1


txt_file.close()