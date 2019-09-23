from maya import cmds, mel
import maya.api.OpenMaya as om2


def find_input_mesh_dagpath(clothnode_name):
    input_meshes = cmds.listConnections(
        clothnode_name + '.inputMesh', shapes=True, type='mesh')
    if not input_meshes:
        raise ValueError('no input mesh found for {}'.format(clothnode_name))
    dependnode = om2.MSelectionList().add(input_meshes[0]).getDependNode(0)
    return om2.MFnDagNode(dependnode)


def find_output_mesh_dagpath(clothnode_name):
    history = cmds.listHistory(clothnode_name, future=True)
    output_meshes = cmds.ls(history, dag=True, type='mesh')
    if not output_meshes:
        raise ValueError('no output mesh found for {}'.format(clothnode_name))
    dependnode = om2.MSelectionList().add(output_meshes[0]).getDependNode(0)
    return om2.MFnDagNode(dependnode)


def clean_inputmesh_connection(clothnode_name):
    input_plug = clothnode_name + '.inputMesh'
    connections = cmds.listConnections(input_plug, plugs=True)
    if not connections:
        return
    cmds.disconnectAttr(connections[0], input_plug)