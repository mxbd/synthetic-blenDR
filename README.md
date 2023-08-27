# synthetic-blenDR
Blender-based Synthetic Image and Annotation Generation using Domain Randomization for Deep Neural Network Object Detection

## Synthetic Data and Domain Randomization

Various challenges within industrial AI arise due to inadequate data availability. This deficiency can manifest in the form of limited dataset sizes or the prohibitively high costs linked to manual annotation. To address these issues, the adoption of synthetic data for training deep learning models has gained significant traction. However, it's worth noting that models exclusively trained on synthetic data often encounter performance deterioration when applied to real-world input. This degradation can be attributed to the inherent disparities between the characteristics of synthetic and real images.

To overcome this limitation, Domain Randomization has emerged as a systematic strategy for data generation. Its primary objective is to bolster model performance in real-world settings by artificially expanding the parameter space of the synthetic training dataset, thus enhancing its transferability to real-world scenarios.
 
## Requirements

| Software | Link |
| ------ | ------ |
| zpy | [zpy GitHub Repository](https://github.com/ZumoLabs/zpy) |
| Blender 2.92 | [Blender Download](https://download.blender.org/release/) |


## Usage

- Gather resources
  - stl files of assembly
  - textures
  - backgrounds
      
- Configure ```config.json ```
  - specify neccesary directories
  - add assembly component structure
  - specify render settings

```sh
python render.py
```


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

<img src="/examples/detection.gif">
