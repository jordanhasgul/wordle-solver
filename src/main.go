package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"strings"
	"time"
)

type Wordle struct {
	word      string
	guessCntr int
}

func NewWordle() *Wordle {
	wordsFile := "data/words.txt"

	rawBytes, err := ioutil.ReadFile(wordsFile)
	if err != nil {
		panic(err)
	}

	words := strings.Split(string(rawBytes), "\n")
	word := words[int(time.Now().UnixNano()%int64(len(words)))]

	return &Wordle{word: word, guessCntr: 0}
}

func (wordle *Wordle) Guess(guess string) Result {
	var resp Result

	for i := 0; i < len(wordle.word); i++ {
		if wordle.word[i] == guess[i] {
			resp[i] = rightLetterRightPosition
		} else if strings.Contains(wordle.word, string(guess[i])) {
			resp[i] = rightLetterWrongPosition
		} else {
			resp[i] = wrongLetter
		}
	}

	wordle.guessCntr += 1
	return resp
}

type Result [5]string

const rightLetterRightPosition string = "g"
const rightLetterWrongPosition string = "y"
const wrongLetter string = "."

func (r Result) String() string {
	strResult := ""
	for i := 0; i < 5; i++ {
		strResult = fmt.Sprintf("%s%s", strResult, r[i])
	}

	return strResult
}

func main() {
	iterations := 100

	totalGuesses := 0
	for i := 0; i < iterations; i++ {
		wordle := NewWordle()
		Solve(wordle)

		totalGuesses += wordle.guessCntr
	}
	average := float64(totalGuesses) / float64(iterations)
	fmt.Printf("AVERAGE %.2f\n", average)
}

type Node struct {
	Guess    string `json:"guess"`
	Results  string `json:"results"`
	Children []Node `json:"children"`
}

func Solve(wordle *Wordle) {
	file, _ := ioutil.ReadFile("data/tree.json")

	var root Node
	err := json.Unmarshal([]byte(file), &root)
	if err != nil {
		panic(err)
	}

	result := wordle.Guess(root.Guess)
	for result.String() != "ggggg" {
		for _, child := range root.Children {
			if child.Results == result.String() {
				root = child
				break
			}
		}

		result = wordle.Guess(root.Guess)
	}
}
