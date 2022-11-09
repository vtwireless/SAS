from typing import Optional, List


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def levelOrder(self, root: Optional[TreeNode]) -> List[List[int]]:
        if not root:
            return []

        returnable = []
        index, nodes_in_layer = 0, 1
        while index <= len(root) - 1:
            target_list = root[index: index + nodes_in_layer]
            if None not in target_list:
                returnable.append(target_list)
            else:
                returnable.append([x for x in target_list if x is not None])

            index += nodes_in_layer
            nodes_in_layer *= 2

        return returnable


def main():
    # input = [3, 9, 20, None, None, 15, 7]
    input = [3, 7, 12, -2, 1, None, None, None, None, 6, 5, None, None, None, None]
    sol = Solution()
    print(sol.levelOrder(input))


if __name__ == '__main__':
    main()
