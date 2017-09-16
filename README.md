# Car-ND Semantic Segmentation
This is my achievement for the Term 3 project 2 for Car-ND.

## 1 Run
Run the following command to run the project:
```
python main.py
```

## 2 Implementation

### 2.1 FCN Skip Layer Architecture
![skip.png](skip.png)
Following the original paper [Fully Convolutional Networks for Semantic Segmentation](https://arxiv.org/pdf/1605.06211.pdf), I implement the skip layer architecture  illustrated above. See the code in [`main.py`](main.py). 

### 2.2 Another Network Architecture
Instead of following a simple FCN structure introduced in the class, I tried some techniques inspired from the literature.

The main idea of my network structure is to **concatenate feature maps with different size:** Such a structure is inspired from the [Pyramid Scene Parsing Network (PSPNet)](https://arxiv.org/abs/1612.01105). Unlike PSPNet, I directly concatenated feature maps with different size instead of a pyramid pooling module. While the intuition is that the segmentation result combines both high-level semantics and low-level features. **What's more**, I also concatenate convolved feature maps at the half level of input image resolution. With only one or two layers of convolution, the feature maps should represent smoothed outline between objects. This is inspired from [this paper](http://cn.arxiv.org/abs/1411.6228). I used convolution layers instead of their *smoothing prior*  Luckily, after several epochs of training, the result show good edges of the road.

See [`main_old.py`](main_old.py) for detailed implementation. I made some changes to the `layers()` and `project_tests_old.test_layers()` functions, since I added `vgg_input_tensor` as an input param.

### 2.3 Training Strategy
- The initial `learning rate` was set to be `1e-4`, and decrease with steps when training certain epochs. Total number of training epochs was 30.
- `AdamOptimizer` was adopted.
- `batch_size` was set to be only 1. This leads to fastest convergence to a semantic segmentation task.

## 3 Performance
Luckily, I found my model performance was very good, with fine outline of the road and no large misclassified regions. Here are some examples below:

**FCN Skip Layer Architecture Results**

![pic1](runs/1505525477.7859635/um_000000.png)
![pic2](runs/1505525477.7859635/umm_000008.png)
![pic3](runs/1505525477.7859635/uu_000024.png)

As for comparison, I presented the results of the other architecture design by myself.

![pic1](runs/1505428016.559246/um_000000.png)
![pic2](runs/1505428016.559246/umm_000008.png)
![pic3](runs/1505428016.559246/uu_000024.png)
