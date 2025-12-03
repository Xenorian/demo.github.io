<template>
  <div class="sidebar-form-container">
    <el-form :model="formData" label-position="top" class="rule-form">
      <el-form-item label="规则名称 (name)">
        <el-input v-model="formData.name" placeholder="规则名称" />
      </el-form-item>

      <el-form-item label="描述 (description)">
        <el-input v-model="formData.description" type="textarea" :rows="2"
          placeholder="例如：检测工人是否佩戴安全帽，或者是否有未经授权的人员进入禁区..." />
      </el-form-item>

      <el-form-item label="类别 (category)">
        <el-input v-model="formData.category" placeholder="security, safety, general..." />
      </el-form-item>

      <el-form-item label="严重程度 (severity)">
        <el-radio-group v-model="formData.severity" size="small" class="custom-radio-group">
          <el-radio-button label="low">Low</el-radio-button>
          <el-radio-button label="medium">Medium</el-radio-button>
          <el-radio-button label="high">High</el-radio-button>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="示例图片/视频 (urls)">
        <div class="upload-area">
          <div v-for="(url, index) in formData.urls" :key="index" class="media-preview-item">
            <template v-if="isImage(url)">
              <el-image :src="url" fit="cover" class="media-preview-img"
                :preview-src-list="formData.urls.filter(isImage)"
                :initial-index="formData.urls.filter(isImage).indexOf(url)" />
            </template>
            <template v-else-if="isVideo(url)">
              <video :src="url" controls class="media-preview-video"></video>
            </template>
            <div class="delete-overlay" @click="removeMedia(index)">
              <el-icon>
                <Delete />
              </el-icon>
            </div>
          </div>

          <el-upload class="media-uploader" :show-file-list="false" :on-change="handleMediaChange"
            :before-upload="beforeMediaUpload" multiple accept="image/*,video/*" action="#" :auto-upload="false"
            list-type="picture-card">
            <el-icon>
              <Plus />
            </el-icon>
          </el-upload>

        </div>
        <p class="upload-tip">支持图片和视频，点击 '+' 上传，悬停在媒体上点击删除图标移除。</p>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref,defineModel, defineProps } from 'vue';
import { Plus, Delete } from '@element-plus/icons-vue'; // 假设你已正确导入 Element Plus Icon
import { ElMessage } from 'element-plus'

const formData = defineModel({
    type: Object,
    required: true,
});


// 检查是否是图片 URL
const isImage = (url) => {
  if (typeof url !== 'string') return false;
  // 增加 data:image/ 检查以支持 base64 图片
  return /^data:image\/|(\.(jpeg|jpg|png|gif|webp))$/i.test(url.split('?')[0]);
};

// 检查是否是视频 URL
const isVideo = (url) => {
  if (typeof url !== 'string') return false;
  // 增加 data:video/ 检查以支持 base64 视频
  return /^data:video\/|(\.(mp4|webm|ogg))$/i.test(url.split('?')[0]);
};

// 文件变化时的处理 (适用于非自动上传)
const handleMediaChange = (file) => {
  // 仅处理文件，实际应用中可能需要向后端上传
  // 限制文件数量，防止用户上传过多
  if (formData.value.urls.length >= 6) {
    console.log("最多只能上传 6 个媒体文件");
    return;
  }

  if (file.raw) {
    const reader = new FileReader();
    reader.onload = (e) => {
        // 1. 存储 Base64/Blob URL 用于预览 (formData.urls)
        formData.value.urls.push(e.target.result); 
        // 2. 存储原始 File 对象用于 Axios 提交 (rawFiles)
        formData.value.rawFiles.push(file.raw);
    };
    // 注意：这里仍然使用 DataURL 只是为了**前端预览**！
    reader.readAsDataURL(file.raw); 
  }
};

// 上传前检查文件类型 (非必要，但能提供即时反馈)
const beforeMediaUpload = (rawFile) => {
  if (!['image/jpeg', 'image/png', 'image/gif', 'video/mp4', 'video/webm', 'video/ogg'].includes(rawFile.type)) {
    // 实际应用中建议使用 ElMessage 提示用户
    ElMessage.error('媒体文件必须是 JPG/PNG/GIF 图片或 MP4/WebM/OGG 视频!')
    return false;
  }
  return true;
};

// 移除媒体文件
const removeMedia = (index) => {
    // 移除 formData.urls 中的预览 URL
    formData.value.urls.splice(index, 1);
    // 同时移除 rawFiles 中的原始文件对象
    formData.value.rawFiles.splice(index, 1);
};

</script>

<style scoped>
/* 省略未修改的部分样式，只保留上传相关的修改 */

.sidebar-form-container {

  padding: 10px 0;

  border-bottom: 1px solid var(--el-border-color-lighter);

  margin-bottom: 15px;

}



.rule-form :deep(.el-form-item) {

  margin-bottom: 15px;

}



.rule-form :deep(.el-form-item__label) {

  font-weight: bold;

  color: #303133;

}



/* 严重程度 Radio Button 组 */

.rule-form :deep(.el-radio-button__inner) {

  padding: 8px 15px;

}



/* 使用深度选择器穿透 scoped 样式 */

/* 分别设置不同选项 */

:deep(.custom-radio-group .el-radio-button:nth-child(1).is-active .el-radio-button__inner) {

  background-color: #409eff !important;

  border-color: #409eff !important;

  box-shadow: -1px 0 0 0 #409eff !important;
  /* 阴影颜色与边框一致 */

}



:deep(.custom-radio-group .el-radio-button:nth-child(2).is-active .el-radio-button__inner) {

  background-color: #ffb341 !important;

  border-color: #ffb341 !important;

  box-shadow: -1px 0 0 0 #ffb341 !important;

}



:deep(.custom-radio-group .el-radio-button:nth-child(3).is-active .el-radio-button__inner) {

  background-color: #ff6666 !important;

  border-color: #ff6666 !important;

  box-shadow: -1px 0 0 0 #ff6666 !important;

}

/* 媒体上传区域布局 */
.upload-area {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  /* 调整间距 */
  align-items: flex-start;
}

/* 媒体项的统一尺寸 */
.media-preview-item,
/* 覆盖 el-upload 的默认尺寸使其与预览项一致 */
.media-uploader :deep(.el-upload--picture-card) {
  width: 100px;
  height: 100px;
  border-radius: 6px;
  /* 保持一致的圆角 */
  margin: 0;
  /* 移除可能的默认外边距 */
}

/* 上传按钮本身的容器 */
.media-uploader {
  line-height: 100px;
}

.media-preview-item {
  position: relative;
  overflow: hidden;
  border: 1px solid var(--el-border-color);
}

.media-preview-img,
.media-preview-video {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
}

.delete-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.3s;
}

.media-preview-item:hover .delete-overlay {
  opacity: 1;
}

.delete-overlay .el-icon {
  color: white;
  font-size: 20px;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 10px;
  /* 调整提示文字的位置 */
}
</style>