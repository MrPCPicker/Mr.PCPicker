<template>
    <div>
        <input type="checkbox" name="todo-text" v-model="isDone">
        <label for="todo-text">{{ todo.text }}</label>
        <button @click = 'deleteTodo(todo.id)'>삭제</button>
    </div>
</template>

<script setup>
const props = defineProps({
    todo : Object,
})

import { useCounterStore } from '@/stores/counter';
import { ref, watch } from 'vue'
const store = useCounterStore()
const deleteTodo = function(selectedId){
    store.deleteTodo(selectedId)
}

const isDone = ref(props.todo.isDone)
watch(isDone, () => {
    store.updateTodo(props.todo.id)
}) 
</script>

<style scoped>

</style>