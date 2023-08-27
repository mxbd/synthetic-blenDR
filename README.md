# synthetic-blenDR
Blender-based Synthetic Image and Annotation Generation using Domain Randomization for Deep Neural Network Object Detection

## Requirements

| Software | Link |
| ------ | ------ |
| zpy | [zpy GitHub Repository](https://github.com/ZumoLabs/zpy) |
| Blender 2.92 | [Blender 2.92 Download](https://download.blender.org/release/) |


## Examples of generated images

<table>
  <tr>
    <th>RGB Image</th>
    <th>Segmentation Image</th>
  </tr>
  <tr>
    <td align="center"><img src="/examples/rgb_image_001.png" alt="Image" style="width:100%;"></td>
    <td align="center"><img src="/examples/iseg_image_001.png" alt="Image" style="width:100%;"></td>
  </tr>
  <tr>
    <td align="center"><img src="/examples/rgb_image_002.png" alt="Image" style="width:100%;"></td>
    <td align="center"><img src="/examples/iseg_image_002.png" alt="Image" style="width:100%;"></td>
  </tr>
  <tr>
    <td align="center"><img src="/examples/rgb_image_003.png" alt="Image" style="width:100%;"></td>
    <td align="center"><img src="/examples/iseg_image_003.png" alt="Image" style="width:100%;"></td>
  </tr>
  <tr>
    <td align="center"><img src="/examples/rgb_image_004.png" alt="Image" style="width:100%;"></td>
    <td align="center"><img src="/examples/iseg_image_004.png" alt="Image" style="width:100%;"></td>
  </tr>
</table>

## Real-time Detection
The following Gif shows real time detection of the assembly using YOLOv7 which was trained on a purely synthetic dataset consisting of 500 training and 130 validation images.
![](/examples/detection.gif)
