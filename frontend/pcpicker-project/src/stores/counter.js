import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useCounterStore = defineStore('counter', () => {
  let id = 0

  const todos = ref([
    {id : id++, text: '할 일 1', isDone: false},
    {id : id++, text: '할 일 2', isDone: false}
  ])

  const addTodo = function(todoText) {
    todos.value.push({
      id: id++,
      text: todoText,
      isDone: false
    })
  }

  const deleteTodo = function(selectedId) {
    todos.value = todos.value.filter(todo => todo.id!== selectedId)
  }

  const updateTodo = function(selectedId){
    todos.value.forEach((todo) => {
      if(todo.id === selectedId) {
        todo.isDone = !todo.isDone
      }
    })
  }

  const doneTodosCount = computed( () => {
    const doneTodos = todos.value.filter((todo) => todo.isDone)
    return doneTodos.length
  }) 

  return { todos, addTodo, deleteTodo, updateTodo, doneTodosCount }
}, {persist : true })
