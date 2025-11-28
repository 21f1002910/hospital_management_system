<!-- AdminLayout.vue or wherever your admin wrapper is -->
<template>
  <div class="admin-layout">
    <nav>
      <!-- Your admin navigation -->
    </nav>
    
    <main>
      <router-view />  <!-- THIS IS CRITICAL - child routes render here -->
    </main>
  </div>
</template>