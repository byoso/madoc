<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <!-- favicon example -->
  <link rel="icon" href="https://i.goopics.net/lhw9s2.png">
  <title>Documentation</title>
  <!-- bulma -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css">
  <!-- vue.js 3 -->
  <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
  <!-- markdown converter to html (cdn) -->
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
</head>
<body>

<div class="" id="app">

<div class="columns">
  <aside class="menu">
    <h1 class="title">Documents</h1>
    <ul>
      <li v-for="page in pages" :key="page">
        <button @click="display(page)" class="button is-fullwidth has-text-left">{{ page.name }}</button>
      </li>
    </ul>

  </aside>
  <div class="column content-col">
    <div class="content" v-html="content_displayed">
    </div>

  </div>
</div>


</div>


</body>

<script>
  const { createApp } = Vue

  createApp({
    data() {
      return {
        pages: