import { Capacitor } from '@capacitor/core';
import { Filesystem } from '@capacitor/filesystem';
import { Storage } from '@capacitor/storage';
import { Share } from '@capacitor/share';
import { Preferences } from '@capacitor/preferences';

window.addEventListener('DOMContentLoaded', () => {
    console.log('vdownloader app initialized');
    console.log('Capacitor platform:', Capacitor.getPlatform());
});