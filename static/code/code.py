print("

if __name__ == "__main__":
    line = input()
    line = str(line).replace("\n","")
    input = line.split(" ")

    index = 0

    size = int(input[index])
    index = index + 1

    list = []

    for i in range(0,size):
        ele = int(input[index])
        index = index + 1
        list.append(ele)

    ans = solve(list)

    print(ans)
    