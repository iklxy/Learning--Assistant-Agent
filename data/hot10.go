import(
    "io"
)
func subarraySum(nums []int, k int) int {
    var current_sum int=0
    var count int=0

    mp :=map[int]int{
        0 : 1
    }

    for _,value range := nums{
        current_sum+=value

        target := current_sum-k

        count+=mp[target]

        mp[current_sum]++
    }

    return count
}