# Ricky Lin and Kevin Wang Period 4

## Classical Dream Team

### List of features implemented 

- lighting
- mesh
- shading

For lighting, mesh, and shading, use the commands specified in the mdl.spec. 

Lighting is called using: 

```
light nameOfLight x y z r g b 
```

This command allows for the manual creation of multiple light sources. 

Shading is called with:

```
shading shadingType
```

If shading is not given, the default shading type is flat. Other types of shading that the user can use are gouraud and phong. 

Mesh is called as: 

```
mesh :name.obj
```

If you have an .obj file in the directory, you replace the name with the name of the obj file. Currently, our mesh command only works for files with both v (vertex) and f (face) lines. If only one is provided, it will not draw anything. Our mesh command also does not recognize more complex obj lines than v and f like vn. Since many things that we are drawing using mesh files are extremely small as defined in their obj files, we multiplied the points by 10 to make them clearly visible.  
