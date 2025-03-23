# make_element_standard.py
# Extract model from postprocess file into a editable model.

# Copyright (c) 2024 Sibo Qiu and Ping Qiu. All rights reserved.
# This software is licensed under the "All Rights Reserved" license.
# Redistribution and use are permitted only under the terms specified
# in the LICENSE.md file provided with this software.
# See LICENSE.md for full license details.


from py_mentat import *
from py_post import *

import re


# ========================== 初始化变量配置 ========================== #
# ====================== Initialize Variables ====================== #

# 后处理文件的绝对路径？（！反斜杠‘\’应写为‘\\’进行转义！）
# Absolute path of post file: (‘\’ should be written as ‘\\’ for escape!)
default_post_path = "C:\\marc\\test-3d_job1.t16"

# 后处理报告文件的绝对路径？（！反斜杠‘\’应写为‘\\’进行转义！）
# Absolute path of post report file: (‘\’ should be written as ‘\\’ for escape!)
default_report_path = "C:\\marc\\test-3d_job1.rpt"

# 要处理后处理的第几步？（应为程序标识步加1）
# Which step of post process to be processed? (Should be step number + 1)
step = 11

# 后处理变形后坐标文本文件绝对路径？（！反斜杠‘\’应写为‘\\’进行转义！）
# Absolute path of output coordinate text file: (‘\’ should be written as ‘\\’ for escape!)
coord_output_path = 'C:\\marc\\output_fmt.txt'

# ====================== Initialize Variables ====================== #
# ========================== 初始化变量配置 ========================== #

# vvvvvvvvvvvvvvvvvvvvvvvvvvvv 调试用函数 vvvvvvvvvvvvvvvvvvvvvvvvvvvv #
# vvvvvvvvvvvvvvvvvvvvvvvvv Debug Functions vvvvvvvvvvvvvvvvvvvvvvvvv #

# Load a post file and save as coordinate list file with index
# 从后处理文件中读取节点坐标并保存为单独的文本文档
def save_post_node_list(post_file_path=default_post_path, dst=coord_output_path):
	# Open postprocess file
	# 打开后处理文件
	p = post_open(post_file_path)
	p.moveto(step)

	# Initialize variables
	# 初始化变量
	data = []
	# Total node counter
	# 总节点计数器
	num = p.nodes()

	for k in range(0, num):
		# Get original coordinate of each node
		# 取得每个节点的原始坐标
		pk = p.node(k)
		# Get 3-axis displacement of each node
		# 取得每个节点的三轴位移
		dx, dy, dz = p.node_displacement(k)
		# data.append([pk.x, pk.y, dx, dy])
		# data.append([pk.x + dx, pk.y + dy, 0])
		# Append the displaced 3-axis coordinate to variable
		# 将位移后的三轴坐标附加到变量中
		data.append([k + 1, pk.x + dx, pk.y + dy, pk.z + dz])

	# Write coordinates to file
	# 将坐标写入文件
	with open(dst, 'w') as file:
		for index in range(0, num):
			wbuf = "{}\t\t{}\t\t{}\t\t{}\n".format(data[index][0], data[index][1], data[index][2], data[index][3])
			file.write(wbuf)


# Read a coordinate list file, file come with save sequence index, return a list
# 读取一个预制的节点表文件，文件带有每个节点的序号。返回一个list列表。
def read_node_list(path=coord_output_path):
	# Initialize variables
	# 初始化变量
	node_list = []

	# Read file
	# 读文件
	with open(path, 'r') as file:
		for line in file:
			# Trim and split the line
			# 修剪去除字符串前后端字符，并分割
			elements = line.strip().split()
			# Convert each element to specific type
			# 为每一个元素进行类型转换
			elements = [int(elements[0])] + [float(e) for e in elements[1:]]
			# Append to node list
			# 附加到节点表中
			node_list.append(elements)

	return node_list

# ^^^^^^^^^^^^^^^^^^^^^^^^^^ Debug Functions ^^^^^^^^^^^^^^^^^^^^^^^^^^ #
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 调试用函数 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ #


# Read coordinate list by processing a post file, return a list
# 从后处理文件读取节点坐标。返回一个list列表。
def get_node_from_post(path=default_post_path):
	# Open post file
	# 打开文件
	try:
		p = post_open(path)
	except:
		print("Bad post file opening.")
	# Move to the step to be processed
	# 移动到被处理的计算步
	p.moveto(step)

	# Initialize variables
	# 初始化变量
	data = []
	num = p.nodes()

	for k in range(0, num):
		# Get original coordinate of each node
		# 取得原始坐标
		pk = p.node(k)
		# Get 3-axis displacement of each node
		# 取得三轴位移量
		dx, dy, dz = p.node_displacement(k)
		# Append the displaced 3-axis coordinate to variable
		# 将位移后的三轴坐标附加到变量中
		data.append([k + 1, pk.x + dx, pk.y + dy, pk.z + dz])

	return data


# Load full report file into string variable
# 将报告文件完整加载入字符串变量
def load_file_full(file_path=default_report_path):
	try:
		with open(file_path, 'r') as file:
			file_content = file.read()
		return file_content
	except Exception as e:
		print(f"Error reading file: {e}")
		return None


# Extract connectivity of each element from report file
# 从报告文件提取每个单元中节点连接关系
def extract_connectivity(file_content):
	# Match "Connectivity:" using regular expression
	# 使用正则表达式匹配 "Connectivity:"
	pattern = re.compile(r'Connectivity:\s*([\d\s]+)')
	matches = pattern.findall(file_content)

	# Extract and convert each group of numbers to list
	# 提取并将每组数字转化为列表
	connectivity_groups = []
	for match in matches:
		numbers = list(map(int, match.split()))
		connectivity_groups.append(numbers)

	return connectivity_groups


# Mentat: Add notes
# Mentat: 添加节点
def make_nodes(node_list):
	for i in range(0, len(node_list)):
		str = "*add_nodes %f %f %f" % (node_list[i][1], node_list[i][2], node_list[i][3])
		py_send(str)


# Mentat: Add elements
# Mentat: 添加单元
# !!!!! Attention: Refer to geometric type of the unit !!!!!
# !!!!! 注意：应按照单元的几何类别添加 !!!!! #
def make_elements(element_list):
	py_send('*set_element_class hex8')
	py_send('*add_elements')
	# range(x, y) represents from x to y - 1, i.e. [x, y)
	# range(x, y)表示从x到y - 1，即 [x, y)
	for index in range(0, 8):
		# Consist with the number of nodes of each unit
		# 此处应与每一个单元共有几个节点保持一致
		cmd = "%d %d %d %d %d %d %d %d " % (element_list[index][0], element_list[index][1], element_list[index][2], element_list[index][3], element_list[index][4], element_list[index][5], element_list[index][6], element_list[index][7])
		py_send(cmd)
	py_send(" # ")

	py_send('*set_element_class penta6')
	py_send('*add_elements')
	# range(x, y) represents from x to y - 1, i.e. [x, y)
	# range(x, y)表示从x到y - 1，即 [x, y)
	for index in range(8, 14):
		# Consist with the number of nodes of each unit
		# 此处应与每一个单元共有几个节点保持一致
		cmd = "%d %d %d %d %d %d " % (element_list[index][0], element_list[index][1], element_list[index][2], element_list[index][3], element_list[index][4], element_list[index][5])
		py_send(cmd)
	py_send(" # ")


def main():
	node_list = get_node_from_post(default_post_path)
	element_list = extract_connectivity(load_file_full(default_report_path))
	make_nodes(node_list)
	make_elements(element_list)

	# Renumber all nodes and meshes
	# 重新编号所有节点和网格
	py_send("*remove_unused_nodes")
	py_send('*renumber_all')


if __name__ == '__main__':
	py_connect('localhost','40007')
	main()
	py_disconnect()
