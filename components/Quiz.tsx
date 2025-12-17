'use client'

import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { CheckCircle, XCircle, Eye, EyeOff, RotateCcw } from 'lucide-react'
import { apiClient, type QuizResponse, type QuizQuestion } from '@/lib/api'
import { cn } from '@/lib/utils'

interface QuizProps {
  docId?: string
  topic?: string
}

interface QuizState {
  questions: QuizQuestion[]
  currentQuestion: number
  answers: Record<number, string>
  showAnswers: boolean
  score: number
  completed: boolean
}

export function Quiz({ docId, topic }: QuizProps) {
  const [quizState, setQuizState] = useState<QuizState>({
    questions: [],
    currentQuestion: 0,
    answers: {},
    showAnswers: false,
    score: 0,
    completed: false,
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const generateQuiz = async () => {
    setLoading(true)
    setError(null)

    try {
      const response: QuizResponse = await apiClient.generateQuiz(docId, topic, 10)
      setQuizState({
        questions: response.questions,
        currentQuestion: 0,
        answers: {},
        showAnswers: false,
        score: 0,
        completed: false,
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate quiz')
    } finally {
      setLoading(false)
    }
  }

  const handleAnswerSelect = (answer: string) => {
    setQuizState(prev => ({
      ...prev,
      answers: {
        ...prev.answers,
        [prev.currentQuestion]: answer,
      },
    }))
  }

  const nextQuestion = () => {
    if (quizState.currentQuestion < quizState.questions.length - 1) {
      setQuizState(prev => ({
        ...prev,
        currentQuestion: prev.currentQuestion + 1,
      }))
    } else {
      setQuizState(prev => ({
        ...prev,
        completed: true,
      }))
    }
  }

  const prevQuestion = () => {
    if (quizState.currentQuestion > 0) {
      setQuizState(prev => ({
        ...prev,
        currentQuestion: prev.currentQuestion - 1,
      }))
    }
  }

  const toggleAnswers = () => {
    setQuizState(prev => ({
      ...prev,
      showAnswers: !prev.showAnswers,
    }))
  }

  const calculateScore = () => {
    let correct = 0
    quizState.questions.forEach((question, index) => {
      if (quizState.answers[index] === question.answer) {
        correct++
      }
    })
    return correct
  }

  const resetQuiz = () => {
    setQuizState({
      questions: [],
      currentQuestion: 0,
      answers: {},
      showAnswers: false,
      score: 0,
      completed: false,
    })
  }

  const getQuestionTypeLabel = (type: string) => {
    switch (type) {
      case 'short_answer':
        return 'Short Answer'
      case 'multiple_choice':
        return 'Multiple Choice'
      case 'cloze':
        return 'Fill in the Blank'
      default:
        return type
    }
  }

  const isCorrect = (questionIndex: number) => {
    return quizState.answers[questionIndex] === quizState.questions[questionIndex]?.answer
  }

  if (loading) {
    return (
      <Card className="w-full max-w-4xl mx-auto">
        <CardContent className="flex items-center justify-center h-96">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4" />
            <p className="text-muted-foreground">Generating quiz questions...</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="w-full max-w-4xl mx-auto">
        <CardContent className="flex items-center justify-center h-96">
          <div className="text-center">
            <p className="text-destructive mb-2">Failed to generate quiz</p>
            <p className="text-sm text-muted-foreground mb-4">{error}</p>
            <Button onClick={generateQuiz}>Try Again</Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (quizState.questions.length === 0) {
    return (
      <Card className="w-full max-w-4xl mx-auto">
        <CardContent className="p-8">
          <div className="text-center">
            <h3 className="text-lg font-semibold mb-2">Generate Quiz</h3>
            <p className="text-muted-foreground mb-6">
              Create a quiz with 10 questions based on your documents
            </p>
            <Button onClick={generateQuiz} size="lg">
              Generate Quiz
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  const currentQuestion = quizState.questions[quizState.currentQuestion]
  const score = calculateScore()

  return (
    <div className="w-full max-w-4xl mx-auto space-y-4">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Quiz</CardTitle>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={toggleAnswers}
              >
                {quizState.showAnswers ? (
                  <>
                    <EyeOff className="h-4 w-4 mr-2" />
                    Hide Answers
                  </>
                ) : (
                  <>
                    <Eye className="h-4 w-4 mr-2" />
                    Show Answers
                  </>
                )}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={resetQuiz}
              >
                <RotateCcw className="h-4 w-4 mr-2" />
                New Quiz
              </Button>
            </div>
          </div>

          <div className="flex items-center space-x-4 text-sm text-muted-foreground">
            <span>Question {quizState.currentQuestion + 1} of {quizState.questions.length}</span>
            <Badge variant="secondary">
              {getQuestionTypeLabel(currentQuestion.type)}
            </Badge>
            {quizState.completed && (
              <span className="text-primary font-medium">
                Score: {score}/{quizState.questions.length}
              </span>
            )}
          </div>
        </CardHeader>
      </Card>

      {/* Question */}
      <Card>
        <CardContent className="p-6">
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium mb-4">
                {currentQuestion.prompt}
              </h3>

              {currentQuestion.type === 'multiple_choice' && currentQuestion.options && (
                <div className="space-y-2">
                  {currentQuestion.options.map((option, index) => (
                    <Button
                      key={index}
                      variant={
                        quizState.answers[quizState.currentQuestion] === option
                          ? 'default'
                          : 'outline'
                      }
                      className={cn(
                        "w-full justify-start text-left",
                        quizState.showAnswers && option === currentQuestion.answer && "bg-green-100 border-green-500 text-green-700",
                        quizState.showAnswers && quizState.answers[quizState.currentQuestion] === option && option !== currentQuestion.answer && "bg-red-100 border-red-500 text-red-700"
                      )}
                      onClick={() => handleAnswerSelect(option)}
                    >
                      <span className="mr-2 font-medium">
                        {String.fromCharCode(65 + index)}.
                      </span>
                      {option}
                      {quizState.showAnswers && option === currentQuestion.answer && (
                        <CheckCircle className="h-4 w-4 ml-auto text-green-600" />
                      )}
                      {quizState.showAnswers && quizState.answers[quizState.currentQuestion] === option && option !== currentQuestion.answer && (
                        <XCircle className="h-4 w-4 ml-auto text-red-600" />
                      )}
                    </Button>
                  ))}
                </div>
              )}

              {currentQuestion.type === 'short_answer' && (
                <div className="space-y-2">
                  <textarea
                    className="w-full p-3 border rounded-md"
                    placeholder="Type your answer here..."
                    value={quizState.answers[quizState.currentQuestion] || ''}
                    onChange={(e) => handleAnswerSelect(e.target.value)}
                    rows={3}
                  />
                  {quizState.showAnswers && (
                    <div className="p-3 bg-muted rounded-md">
                      <p className="text-sm font-medium text-muted-foreground mb-1">
                        Correct Answer:
                      </p>
                      <p className="text-sm">{currentQuestion.answer}</p>
                    </div>
                  )}
                </div>
              )}

              {currentQuestion.type === 'cloze' && (
                <div className="space-y-2">
                  <div className="p-3 border rounded-md">
                    <p className="text-sm">
                      {currentQuestion.prompt.replace('_____', '________')}
                    </p>
                  </div>
                  <input
                    type="text"
                    className="w-full p-3 border rounded-md"
                    placeholder="Fill in the blank..."
                    value={quizState.answers[quizState.currentQuestion] || ''}
                    onChange={(e) => handleAnswerSelect(e.target.value)}
                  />
                  {quizState.showAnswers && (
                    <div className="p-3 bg-muted rounded-md">
                      <p className="text-sm font-medium text-muted-foreground mb-1">
                        Correct Answer:
                      </p>
                      <p className="text-sm">{currentQuestion.answer}</p>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Source */}
            <div className="p-3 bg-muted rounded-md">
              <p className="text-xs text-muted-foreground mb-1">Source:</p>
              <p className="text-sm">Page {currentQuestion.page}</p>
              <p className="text-xs text-muted-foreground mt-1 italic">
                &quot;{currentQuestion.quote}&quot;
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Navigation */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <Button
              variant="outline"
              onClick={prevQuestion}
              disabled={quizState.currentQuestion === 0}
            >
              Previous
            </Button>

            {quizState.completed ? (
              <div className="text-center">
                <p className="text-lg font-medium mb-2">
                  Quiz Complete!
                </p>
                <p className="text-muted-foreground">
                  You scored {score} out of {quizState.questions.length} questions
                </p>
              </div>
            ) : (
              <Button onClick={nextQuestion}>
                {quizState.currentQuestion === quizState.questions.length - 1
                  ? 'Finish Quiz'
                  : 'Next Question'
                }
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
